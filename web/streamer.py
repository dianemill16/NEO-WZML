# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# FileToLink streaming core. The web server runs as its own gunicorn
# process (no TgClient), so this module owns a small pool of Telegram
# clients — the bot token plus every HELPER_TOKEN — and load-balances
# range requests across them. Links are HMAC-signed with a secret both
# processes derive from BOT_TOKEN, so URLs can't be forged.

from asyncio import Lock, sleep
from hashlib import sha256
from hmac import compare_digest, new as hmac_new
from math import ceil, floor
from time import time

from pyrogram import Client, raw, utils
from pyrogram.errors import AuthBytesInvalid, FloodWait
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.session import Auth, Session

from bot.core.config_manager import Config

CHUNK_SIZE = 1024 * 1024


def _secret():
    return sha256(
        (Config.BOT_TOKEN or "neo-wzml").encode()
    ).digest()


def sign(chat_id, message_id):
    """Short signature binding a link to one specific message."""
    payload = f"{chat_id}:{message_id}".encode()
    return hmac_new(_secret(), payload, sha256).hexdigest()[:16]


def verify(chat_id, message_id, token):
    try:
        return compare_digest(sign(chat_id, message_id), str(token))
    except Exception:
        return False


def make_path(chat_id, message_id):
    """URL path component: <message_id>/<sig>"""
    return f"{message_id}/{sign(chat_id, message_id)}"


class StreamClients:
    """Lazily-started Telegram clients used only for streaming."""

    _clients = []
    _loads = {}
    _lock = Lock()
    _started = False

    @classmethod
    async def start(cls):
        async with cls._lock:
            if cls._started:
                return cls._clients
            tokens = [Config.BOT_TOKEN]
            if Config.HELPER_TOKENS:
                tokens += Config.HELPER_TOKENS.split()
            for no, token in enumerate(tokens):
                if not token:
                    continue
                try:
                    client = Client(
                        f"NEO-WZML-Stream{no}",
                        api_id=Config.TELEGRAM_API,
                        api_hash=Config.TELEGRAM_HASH,
                        bot_token=token,
                        proxy=Config.TG_PROXY,
                        in_memory=True,
                        no_updates=True,
                        max_concurrent_transmissions=10,
                    )
                    await client.start()
                    cls._clients.append(client)
                    cls._loads[len(cls._clients) - 1] = 0
                except Exception as e:
                    from logging import getLogger

                    getLogger(__name__).error(
                        f"Stream client {no} failed to start: {e}"
                    )
            cls._started = True
            return cls._clients

    @classmethod
    async def stop(cls):
        async with cls._lock:
            for client in cls._clients:
                try:
                    await client.stop()
                except Exception:
                    pass
            cls._clients = []
            cls._loads = {}
            cls._started = False

    @classmethod
    def pick(cls):
        """Least-loaded client, so concurrent viewers spread across bots."""
        if not cls._clients:
            raise RuntimeError("No stream clients available")
        index = min(cls._loads, key=cls._loads.get)
        return index, cls._clients[index]

    @classmethod
    def acquire(cls, index):
        cls._loads[index] = cls._loads.get(index, 0) + 1

    @classmethod
    def release(cls, index):
        cls._loads[index] = max(0, cls._loads.get(index, 1) - 1)

    @classmethod
    def loads(cls):
        return dict(cls._loads)


class ByteStreamer:
    """Serves byte ranges of a Telegram file over raw upload.GetFile."""

    def __init__(self, client, index):
        self.client = client
        self.index = index
        self._sessions = {}

    _props_cache = {}
    _props_time = {}
    _CACHE_TTL = 30 * 60

    @staticmethod
    def _media(message):
        for attr in (
            "document",
            "video",
            "audio",
            "photo",
            "animation",
            "voice",
            "video_note",
            "sticker",
        ):
            if media := getattr(message, attr, None):
                return media
        return None

    async def get_properties(self, chat_id, message_id):
        """(FileId, file_size, file_name, mime_type) with a short cache."""
        key = (chat_id, message_id)
        now = time()
        if key in self._props_cache and now - self._props_time.get(key, 0) < self._CACHE_TTL:
            return self._props_cache[key]

        message = await self.client.get_messages(chat_id, message_id)
        if not message or message.empty:
            raise FileNotFoundError("Message not found or deleted")
        media = self._media(message)
        if media is None:
            raise FileNotFoundError("Message has no downloadable media")

        props = (
            FileId.decode(media.file_id),
            getattr(media, "file_size", 0) or 0,
            getattr(media, "file_name", "") or f"{message_id}.bin",
            getattr(media, "mime_type", "") or "application/octet-stream",
        )
        self._props_cache[key] = props
        self._props_time[key] = now
        return props

    async def _media_session(self, file_id):
        dc_id = file_id.dc_id
        if dc_id in self._sessions:
            return self._sessions[dc_id]

        client = self.client
        if dc_id != await client.storage.dc_id():
            session = Session(
                client,
                dc_id,
                await Auth(client, dc_id, await client.storage.test_mode()).create(),
                await client.storage.test_mode(),
                is_media=True,
            )
            await session.start()
            for _ in range(6):
                exported = await client.invoke(
                    raw.functions.auth.ExportAuthorization(dc_id=dc_id)
                )
                try:
                    await session.invoke(
                        raw.functions.auth.ImportAuthorization(
                            id=exported.id, bytes=exported.bytes
                        )
                    )
                    break
                except AuthBytesInvalid:
                    await sleep(1)
            else:
                await session.stop()
                raise AuthBytesInvalid
        else:
            session = Session(
                client,
                dc_id,
                await client.storage.auth_key(),
                await client.storage.test_mode(),
                is_media=True,
            )
            await session.start()

        self._sessions[dc_id] = session
        return session

    @staticmethod
    def _location(file_id):
        file_type = file_id.file_type
        if file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = raw.types.InputPeerUser(
                    user_id=file_id.chat_id, access_hash=file_id.chat_access_hash
                )
            else:
                peer = (
                    raw.types.InputPeerChat(chat_id=-file_id.chat_id)
                    if file_id.chat_access_hash == 0
                    else raw.types.InputPeerChannel(
                        channel_id=utils.get_channel_id(file_id.chat_id),
                        access_hash=file_id.chat_access_hash,
                    )
                )
            return raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=file_id.volume_id,
                local_id=file_id.local_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG,
            )
        if file_type == FileType.PHOTO:
            return raw.types.InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        return raw.types.InputDocumentFileLocation(
            id=file_id.media_id,
            access_hash=file_id.access_hash,
            file_reference=file_id.file_reference,
            thumb_size=file_id.thumbnail_size,
        )

    async def yield_file(self, file_id, offset, first_cut, last_cut, part_count):
        """Yield the requested byte range, chunk by chunk."""
        session = await self._media_session(file_id)
        location = self._location(file_id)
        current_part = 1
        fails = 0

        while current_part <= part_count:
            try:
                r = await session.invoke(
                    raw.functions.upload.GetFile(
                        location=location, offset=offset, limit=CHUNK_SIZE
                    )
                )
            except FloodWait as f:
                fails += 1
                if fails > 5:
                    raise
                await sleep(f.value + 1)
                continue
            except (TimeoutError, ConnectionError):
                fails += 1
                if fails > 5:
                    raise
                await sleep(1)
                continue

            if not isinstance(r, raw.types.upload.File):
                raise ValueError(f"Unexpected response: {r}")
            chunk = r.bytes
            if not chunk:
                break

            fails = 0
            if part_count == 1:
                yield chunk[first_cut:last_cut]
            elif current_part == 1:
                yield chunk[first_cut:]
            elif current_part == part_count:
                yield chunk[:last_cut]
            else:
                yield chunk

            current_part += 1
            offset += CHUNK_SIZE

    async def close(self):
        for session in self._sessions.values():
            try:
                await session.stop()
            except Exception:
                pass
        self._sessions.clear()


def range_params(start, end, file_size):
    """Translate an HTTP byte range into GetFile chunk parameters."""
    until_bytes = min(end, file_size - 1)
    offset = start - (start % CHUNK_SIZE)
    first_cut = start - offset
    last_cut = until_bytes % CHUNK_SIZE + 1
    part_count = until_bytes // CHUNK_SIZE - offset // CHUNK_SIZE + 1
    return offset, first_cut, last_cut, part_count
