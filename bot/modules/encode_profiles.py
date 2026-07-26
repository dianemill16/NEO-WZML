# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# /encode — hands the user a signed link to the WebUI encoding-profile
# builder. Profiles saved there land in FFMPEG_CMDS and are used with
# `-ff <profile>` on any leech/mirror task.

from bot import user_data
from bot.core.config_manager import Config
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.message_utils import send_message


@new_task
async def encode_profiles(_, message):
    if message.from_user is None:
        await send_message(message, "Run <code>/encode</code> from a user account.")
        return
    user_id = message.from_user.id
    base_url = (Config.BASE_URL or "").rstrip("/")
    if not base_url:
        await send_message(
            message,
            "<code>BASE_URL</code> is not set — the encoding WebUI needs it.",
        )
        return
    if not Config.DATABASE_URL:
        await send_message(
            message,
            "<code>DATABASE_URL</code> is not set — profiles can't be saved.",
        )
        return

    from web.encode_store import sign_user

    url = f"{base_url}/app/encode-profiles?user={user_id}&token={sign_user(user_id)}"

    existing = (user_data.get(user_id, {}).get("FFMPEG_CMDS") or {}) or (
        Config.FFMPEG_CMDS or {}
    )
    names = ", ".join(f"<code>{n}</code>" for n in list(existing)[:10]) or "none yet"

    buttons = ButtonMaker()
    buttons.url_button("Open Encoding Profiles", url)

    await send_message(
        message,
        "<blockquote><b><i>Encoding Profiles</i></b></blockquote>\n\n"
        "Build FFmpeg presets visually — codec, CRF, resolution, audio, "
        "container — with a live command preview.\n\n"
        f" • <b>Your profiles:</b> {names}\n"
        " • <b>Use:</b> <code>/leech link -ff &lt;profile&gt;</code>\n\n"
        "<i>The link is personal — don't share it.</i>",
        buttons.build_menu(1),
    )
