# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# /link — turn a Telegram file into direct streaming + download URLs
# served by the web process (see web/streamer.py, web/wserver.py).

from bot import LOGGER
from bot.core.config_manager import Config
from bot.core.tg_client import TgClient
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.ext_utils.status_utils import get_readable_file_size
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.message_utils import send_message

_MEDIA_ATTRS = (
    "document",
    "video",
    "audio",
    "photo",
    "animation",
    "voice",
    "video_note",
    "sticker",
)

_STREAMABLE = (
    ".mkv", ".mp4", ".webm", ".avi", ".mov", ".m4v", ".ts", ".flv",
    ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wav",
)


def _get_media(message):
    for attr in _MEDIA_ATTRS:
        if media := getattr(message, attr, None):
            return media
    return None


def _bin_chat():
    # single source of truth shared with the web process — the link
    # signature is bound to this exact value
    from web.streamer import bin_chat

    return bin_chat()


@new_task
async def file_to_link(_, message):
    reply = message.reply_to_message
    if not reply or not _get_media(reply):
        await send_message(
            message,
            "<b>Reply to a file</b> with <code>/link</code> to get direct "
            "streaming and download URLs.",
        )
        return

    if not Config.FILETOLINK_ENABLED:
        await send_message(
            message,
            "FileToLink is disabled. Enable <code>FILETOLINK_ENABLED</code> "
            "in /bsetting.",
        )
        return

    base_url = (Config.BASE_URL or "").rstrip("/")
    if not base_url:
        await send_message(
            message, "<code>BASE_URL</code> is not set — can't build links."
        )
        return

    bin_chat = _bin_chat()
    if not bin_chat:
        await send_message(
            message,
            "Set <code>FILETOLINK_CHAT</code> (or <code>LEECH_DUMP_CHAT</code>) "
            "and make the bot an admin there.",
        )
        return

    try:
        stored = await TgClient.bot.copy_message(
            chat_id=bin_chat,
            from_chat_id=reply.chat.id,
            message_id=reply.id,
            disable_notification=True,
        )
    except Exception as e:
        LOGGER.error(f"FileToLink: failed to store media: {e}")
        await send_message(
            message,
            f"Couldn't store the file in the bin chat — is the bot an admin there?\n<code>{e}</code>",
        )
        return

    from web.streamer import make_path

    media = _get_media(stored)
    file_name = getattr(media, "file_name", "") or "file"
    file_size = getattr(media, "file_size", 0) or 0
    path = make_path(bin_chat, stored.id)

    stream_url = f"{base_url}/stream/{path}"
    download_url = f"{base_url}/dl/{path}"
    watch_url = f"{base_url}/watch/{path}"
    # a directly-sent video/voice note often has no file_name, so fall
    # back to the media type and mime before deciding it isn't playable
    mime = (getattr(media, "mime_type", "") or "").lower()
    streamable = (
        file_name.lower().endswith(_STREAMABLE)
        or mime.startswith(("video/", "audio/"))
        or any(
            getattr(stored, attr, None) is not None
            for attr in ("video", "audio", "voice", "animation", "video_note")
        )
    )

    buttons = ButtonMaker()
    if streamable:
        buttons.url_button("Watch", watch_url)
    buttons.url_button("Download", download_url)

    text = (
        "<blockquote><b><i>Link Generated</i></b></blockquote>\n\n"
        f" • <b>File:</b> <code>{file_name}</code>\n"
        f" • <b>Size:</b> {get_readable_file_size(file_size)}\n\n"
        f" • <b>Download:</b> <a href='{download_url}'>Click Here</a>"
    )
    if streamable:
        text += f"\n • <b>Stream:</b> <a href='{stream_url}'>Click Here</a>"

    await send_message(message, text, buttons.build_menu(2))
