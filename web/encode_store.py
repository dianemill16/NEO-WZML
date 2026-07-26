# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# Builds ffmpeg argument strings from the WebUI encoding profile form and
# persists them into FFMPEG_CMDS (global or per-user), which is the format
# `-ff <profile>` already understands.

from hashlib import sha256
from hmac import compare_digest, new as hmac_new

from bot.core.config_manager import Config

VIDEO_CODECS = {
    "copy": "copy",
    "x264": "libx264",
    "x265": "libx265",
    "av1": "libsvtav1",
    "vp9": "libvpx-vp9",
}
AUDIO_CODECS = {
    "copy": "copy",
    "aac": "aac",
    "opus": "libopus",
    "mp3": "libmp3lame",
    "ac3": "ac3",
}
PRESETS = (
    "ultrafast", "superfast", "veryfast", "faster", "fast",
    "medium", "slow", "slower", "veryslow",
)
RESOLUTIONS = {
    "source": "",
    "2160": "3840:-2",
    "1440": "2560:-2",
    "1080": "1920:-2",
    "720": "1280:-2",
    "480": "854:-2",
    "360": "640:-2",
}
CONTAINERS = ("mkv", "mp4", "webm")


def web_secret():
    return sha256((Config.BOT_TOKEN or "neo-wzml").encode() + b"web").digest()


def sign_user(user_id):
    return hmac_new(web_secret(), str(user_id).encode(), sha256).hexdigest()[:16]


def verify_user(user_id, token):
    try:
        return compare_digest(sign_user(user_id), str(token))
    except Exception:
        return False


def sanitize_extra(extra):
    """Accept free-form extra ffmpeg flags only if every token is safe.
    Rejecting the whole field (rather than filtering token by token)
    avoids leaving mangled fragments in the command."""
    if not extra:
        return ""
    tokens = str(extra).split()
    for part in tokens:
        if any(c in part for c in "&|;><`$\n\r\\\"'"):
            return ""
        if part.startswith("/") or ".." in part:
            return ""
        # input/output and format overrides are owned by the builder
        if part in ("-i", "-y", "-n", "-f"):
            return ""
    return " ".join(tokens)


def build_command(profile):
    """Translate a profile dict from the web form into an ffmpeg arg
    string in FFMPEG_CMDS format (no leading 'ffmpeg', mltb placeholders
    for input/output)."""
    v_codec = VIDEO_CODECS.get(profile.get("video_codec", "copy"), "copy")
    a_codec = AUDIO_CODECS.get(profile.get("audio_codec", "copy"), "copy")
    container = profile.get("container", "mkv")
    if container not in CONTAINERS:
        container = "mkv"

    source = profile.get("source", "video")
    inp = "mltb.video" if source == "video" else f"mltb.{source}"
    args = [f"-i {inp}"]

    # stream mapping
    if profile.get("keep_all_streams", True):
        args.append("-map 0")
    else:
        args.append("-map 0:v:0 -map 0:a? -map 0:s?")

    args.append(f"-c:v {v_codec}")
    if v_codec != "copy":
        crf = profile.get("crf")
        if crf not in (None, ""):
            try:
                crf = max(0, min(63, int(crf)))
                args.append(
                    f"-crf {crf}" if v_codec != "libsvtav1" else f"-crf {crf}"
                )
            except (TypeError, ValueError):
                pass
        preset = profile.get("preset")
        if preset in PRESETS and v_codec in ("libx264", "libx265"):
            args.append(f"-preset {preset}")
        if pix := profile.get("pixel_format"):
            if pix in ("yuv420p", "yuv420p10le", "yuv444p"):
                args.append(f"-pix_fmt {pix}")
        scale = RESOLUTIONS.get(str(profile.get("resolution", "source")), "")
        if scale:
            args.append(f'-vf scale={scale}')
        if v_codec == "libx265":
            args.append("-tag:v hvc1")

    args.append(f"-c:a {a_codec}")
    if a_codec != "copy":
        if bitrate := profile.get("audio_bitrate"):
            if str(bitrate).isdigit():
                args.append(f"-b:a {bitrate}k")

    if profile.get("keep_subs", True):
        args.append("-c:s copy" if container == "mkv" else "-c:s mov_text")
    else:
        args.append("-sn")

    if metadata := profile.get("metadata_title"):
        safe = str(metadata).replace('"', "").replace("\n", " ")[:120]
        args.append(f'-metadata title="{safe}"')

    if extra := sanitize_extra(profile.get("extra_args")):
        args.append(extra)

    args.append(f"mltb.{container}")
    if profile.get("delete_original"):
        args.append("-del")
    return " ".join(args)


def validate_name(name):
    name = str(name or "").strip()
    if not name or len(name) > 40:
        return None
    if not all(c.isalnum() or c in "_-" for c in name):
        return None
    return name
