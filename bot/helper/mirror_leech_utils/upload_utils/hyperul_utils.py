# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# HyperUpload raw helpers: pre-upload file bytes with helper bot clients
# (client.save_file) so several files climb to Telegram in parallel, then
# post each message near-instantly with messages.SendMedia. Posting stays
# strictly sequential in the uploader, so series episodes and split parts
# always land in order while the heavy byte transfer runs concurrently.

from mimetypes import guess_type
from os import path as ospath

from pyrogram import raw
from pyrogram.session.internals import MsgId

from bot import LOGGER


def guess_mime(path, default="application/octet-stream"):
    return guess_type(path)[0] or default


async def parse_caption(client, caption):
    if not caption:
        return "", None
    try:
        parsed = await client.parser.parse(caption)
        return parsed.get("message") or "", parsed.get("entities") or None
    except Exception as e:
        LOGGER.warning(f"HyperUL caption parse failed, sending raw text: {e}")
        return caption, None


def build_uploaded_media(
    kind,
    uploaded_file,
    file_path,
    thumb_file=None,
    duration=0,
    width=0,
    height=0,
    performer=None,
    title=None,
):
    """Build a raw InputMedia* from a pre-uploaded InputFile."""
    if kind == "photo":
        return raw.types.InputMediaUploadedPhoto(file=uploaded_file)

    file_name = ospath.basename(file_path)
    attributes = [raw.types.DocumentAttributeFilename(file_name=file_name)]
    force_file = False

    if kind == "video":
        attributes.append(
            raw.types.DocumentAttributeVideo(
                duration=duration,
                w=width or 480,
                h=height or 320,
                supports_streaming=True,
            )
        )
        mime = guess_mime(file_path, "video/mp4")
    elif kind == "audio":
        attributes.append(
            raw.types.DocumentAttributeAudio(
                duration=duration,
                performer=performer,
                title=title,
            )
        )
        mime = guess_mime(file_path, "audio/mpeg")
    else:
        force_file = True
        mime = guess_mime(file_path)

    return raw.types.InputMediaUploadedDocument(
        file=uploaded_file,
        mime_type=mime,
        attributes=attributes,
        thumb=thumb_file,
        force_file=force_file,
    )


async def raw_send_media(
    client,
    chat_id,
    media,
    caption,
    reply_to_id=None,
    thread_id=None,
):
    """Send a pre-uploaded media via raw SendMedia; return the full
    pyrogram Message (fetched back so all downstream code — links,
    media groups, copy_message — keeps working unchanged)."""
    peer = await client.resolve_peer(chat_id)
    text, entities = await parse_caption(client, caption)

    reply_to = None
    if reply_to_id or thread_id:
        try:
            reply_to = raw.types.InputReplyToMessage(
                reply_to_msg_id=reply_to_id or thread_id,
                top_msg_id=thread_id if reply_to_id else None,
            )
        except Exception:
            reply_to = None

    sent_random_id = MsgId()
    r = await client.invoke(
        raw.functions.messages.SendMedia(
            peer=peer,
            media=media,
            message=text,
            random_id=sent_random_id,
            entities=entities,
            silent=True,
            reply_to=reply_to,
        )
    )

    # Telegram can bundle updates unrelated to this specific send (read
    # receipts, activity from other chats a busy helper bot is also a
    # member of, etc.) into the same Updates container as the one for
    # our own message. Grabbing the first UpdateNewMessage /
    # UpdateNewChannelMessage by type alone — the old behavior — can
    # therefore pick up the WRONG message id, from an entirely different
    # chat, if one happens to be bundled in first. That produces a
    # message id which looks valid at queue time but is later rejected
    # by Telegram as MESSAGE_ID_INVALID when something tries to act on
    # it in what it assumes is chat_id's history.
    #
    # UpdateMessageID maps OUR OWN random_id -> the real message id and
    # is authoritative for identifying our own send; prefer it. Only
    # fall back to a type-based match if that's genuinely absent, and
    # even then, verify the candidate's peer actually matches the chat
    # we sent to before trusting it.
    target_channel_id = getattr(peer, "channel_id", None)
    target_chat_id = getattr(peer, "chat_id", None)
    target_user_id = getattr(peer, "user_id", None)

    msg_id = None
    fallback_msg_id = None
    for update in r.updates:
        if (
            isinstance(update, raw.types.UpdateMessageID)
            and update.random_id == sent_random_id
        ):
            msg_id = update.id
            break
        if isinstance(
            update,
            (raw.types.UpdateNewMessage, raw.types.UpdateNewChannelMessage),
        ):
            msg_peer = getattr(update.message, "peer_id", None)
            belongs_to_target = (
                (target_channel_id is not None
                 and getattr(msg_peer, "channel_id", None) == target_channel_id)
                or (target_chat_id is not None
                    and getattr(msg_peer, "chat_id", None) == target_chat_id)
                or (target_user_id is not None
                    and getattr(msg_peer, "user_id", None) == target_user_id)
            )
            if belongs_to_target:
                fallback_msg_id = update.message.id

    if msg_id is None:
        msg_id = fallback_msg_id

    if msg_id is None:
        raise ValueError("HyperUL: SendMedia returned no message id")

    return await client.get_messages(chat_id=chat_id, message_ids=msg_id)
