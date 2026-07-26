# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# Encoding profiles: the visual builder's data model, validation and
# ffmpeg command generation. Profiles persist into FFMPEG_CMDS (per-user
# or global), which is the format `-ff <name>` already understands, so an
# encode built here runs through the existing task pipeline unchanged.

from hashlib import sha256
from hmac import compare_digest, new as hmac_new

from bot.core.config_manager import Config

# value -> ffmpeg encoder
VIDEO_CODECS = {
    "copy": "copy",
    "libx264": "libx264",
    "libx265": "libx265",
    "libsvtav1": "libsvtav1",
    "libvpx-vp9": "libvpx-vp9",
}
AUDIO_CODECS = {
    "copy": "copy",
    "libopus": "libopus",
    "aac": "aac",
    "libmp3lame": "libmp3lame",
    "ac3": "ac3",
    "flac": "flac",
}
# x264/x265/vp9 take named presets; SVT-AV1 takes 0-13 (lower = slower)
NAMED_PRESETS = (
    "ultrafast", "superfast", "veryfast", "faster", "fast",
    "medium", "slow", "slower", "veryslow",
)
PIX_FMTS = ("", "yuv420p", "yuv420p10le", "yuv422p", "yuv444p", "yuv444p10le")
SUBTITLE_MODES = ("copy", "remove")
CONTAINERS = ("mkv", "mp4", "webm")
RESOLUTIONS = {
    "source": "",
    "2160": "3840:-2",
    "1440": "2560:-2",
    "1080": "1920:-2",
    "720": "1280:-2",
    "480": "854:-2",
    "360": "640:-2",
}
DISPOSITIONS = (
    "0", "default", "forced", "default+forced", "dub", "comment",
    "hearing_impaired", "visual_impaired", "captions",
)

# one-click starting points shown in the builder
TEMPLATES = {
    "av1": {
        "name": "AV1_Archive",
        "video_codec": "libsvtav1",
        "audio_codec": "libopus",
        "container": "mkv",
        "video_params": {"crf": 28, "preset": "4", "pix_fmt": "yuv420p10le"},
        "audio_params": {"bitrate": "128k"},
        "subtitle_mode": "copy",
    },
    "anime": {
        "name": "Anime_Encode",
        "video_codec": "libx265",
        "audio_codec": "libopus",
        "container": "mkv",
        "video_params": {
            "crf": 20,
            "preset": "slow",
            "pix_fmt": "yuv420p10le",
            "extra_params": "tune=animation",
        },
        "audio_params": {"bitrate": "192k"},
        "subtitle_mode": "copy",
    },
    "web": {
        "name": "Web_Streaming",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "container": "mp4",
        "video_params": {
            "crf": 23,
            "preset": "fast",
            "pix_fmt": "yuv420p",
            "profile": "high",
            "level": "4.1",
        },
        "audio_params": {"bitrate": "128k"},
        "subtitle_mode": "copy",
    },
}


def web_secret():
    return sha256((Config.BOT_TOKEN or "neo-wzml").encode() + b"web").digest()


def sign_user(user_id):
    return hmac_new(web_secret(), str(user_id).encode(), sha256).hexdigest()[:16]


def verify_user(user_id, token):
    try:
        return compare_digest(sign_user(user_id), str(token))
    except Exception:
        return False


def validate_name(name):
    name = str(name or "").strip()
    if not name or len(name) > 40:
        return None
    if not all(c.isalnum() or c in "_- " for c in name):
        return None
    return name.replace(" ", "_")


def _clean(value, limit=120):
    """Strip anything that could break out of the argument string."""
    text = str(value or "").strip()
    if not text:
        return ""
    for ch in '&|;><`$\n\r\\"\'':
        text = text.replace(ch, "")
    return text[:limit]


def sanitize_extra(extra):
    """Free-form ffmpeg flags, accepted only if every token is safe.
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


def _codec_params(value):
    """`key=value:key=value` chunks for -x265-params / -svtav1-params."""
    text = _clean(value, 200).replace(" ", "")
    parts = [p for p in text.split(":") if "=" in p]
    return ":".join(parts)


def _map_flags(track_type, spec):
    """Map selectors: '?'/'all' keeps every track, else indices."""
    spec = str(spec or "?").strip() or "?"
    out = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if token in ("?", "*", "all"):
            out.append(f"-map 0:{track_type}?")
        elif token.rstrip("?").isdigit():
            idx = token.rstrip("?")
            out.append(f"-map 0:{track_type}:{idx}?")
    return out


def normalize(profile):
    """Coerce raw form input into the stored profile shape."""
    v_params = profile.get("video_params") or {}
    a_params = profile.get("audio_params") or {}

    v_codec = profile.get("video_codec", "copy")
    if v_codec not in VIDEO_CODECS:
        v_codec = "copy"
    a_codec = profile.get("audio_codec", "copy")
    if a_codec not in AUDIO_CODECS:
        a_codec = "copy"

    container = profile.get("container", "mkv")
    if container not in CONTAINERS:
        container = "mkv"

    sub_mode = profile.get("subtitle_mode", "copy")
    if sub_mode not in SUBTITLE_MODES:
        sub_mode = "copy"

    try:
        crf = v_params.get("crf")
        crf = max(0, min(63, int(crf))) if crf not in (None, "") else None
    except (TypeError, ValueError):
        crf = None

    preset = _clean(v_params.get("preset"), 12)
    if v_codec == "libsvtav1":
        preset = preset if preset.isdigit() and 0 <= int(preset) <= 13 else ""
    elif preset not in NAMED_PRESETS:
        preset = ""

    pix_fmt = v_params.get("pix_fmt", "")
    if pix_fmt not in PIX_FMTS:
        pix_fmt = ""

    resolution = str(profile.get("resolution", "source"))
    if resolution not in RESOLUTIONS:
        resolution = "source"

    bitrate = _clean(a_params.get("bitrate"), 10).lower()
    if bitrate:
        digits = bitrate[:-1] if bitrate.endswith("k") else bitrate
        bitrate = f"{digits}k" if digits.isdigit() else ""

    channels = str(a_params.get("channels") or "").strip()
    channels = channels if channels.isdigit() and 1 <= int(channels) <= 8 else ""

    metadata = {}
    for key, value in (profile.get("metadata") or {}).items():
        key = _clean(key, 40)
        value = _clean(value, 160)
        if key and value:
            metadata[key] = value

    disposition = {}
    for key, value in (profile.get("disposition") or {}).items():
        key = _clean(key, 20)
        value = str(value or "").strip()
        if key and value in DISPOSITIONS:
            disposition[key] = value

    tracks = profile.get("tracks") or {}
    return {
        "name": validate_name(profile.get("name")) or "",
        "video_codec": v_codec,
        "audio_codec": a_codec,
        "container": container,
        "subtitle_mode": sub_mode,
        "resolution": resolution,
        "video_params": {
            "crf": crf,
            "preset": preset,
            "pix_fmt": pix_fmt,
            "profile": _clean(v_params.get("profile"), 20),
            "level": _clean(v_params.get("level"), 8),
            "extra_params": _codec_params(v_params.get("extra_params")),
            "color_primaries": _clean(v_params.get("color_primaries"), 20),
            "color_trc": _clean(v_params.get("color_trc"), 20),
            "colorspace": _clean(v_params.get("colorspace"), 20),
        },
        "audio_params": {
            "bitrate": bitrate,
            "channels": channels,
            "vbr": bool(a_params.get("vbr")),
        },
        "tracks": {
            "video": _clean(tracks.get("video"), 20) or "0",
            "audio": _clean(tracks.get("audio"), 20) or "?",
            "subtitle": _clean(tracks.get("subtitle"), 20) or "?",
        },
        "metadata": metadata,
        "disposition": disposition,
        "extra_args": sanitize_extra(profile.get("extra_args")),
        "delete_original": bool(profile.get("delete_original")),
        "is_default": bool(profile.get("is_default")),
    }


def build_command(profile):
    """Translate a profile into an ffmpeg arg string in FFMPEG_CMDS
    format (no leading 'ffmpeg'; mltb placeholders for input/output)."""
    p = normalize(profile)
    v_codec = p["video_codec"]
    a_codec = p["audio_codec"]
    v = p["video_params"]
    a = p["audio_params"]
    container = p["container"]

    args = ["-i mltb.video"]
    args += _map_flags("v", p["tracks"]["video"])
    args += _map_flags("a", p["tracks"]["audio"])
    if p["subtitle_mode"] == "copy":
        args += _map_flags("s", p["tracks"]["subtitle"])
    if container == "mkv":
        args.append("-map 0:t?")

    args.append(f"-c:v {v_codec}")
    if v_codec != "copy":
        if v["pix_fmt"]:
            args.append(f"-pix_fmt {v['pix_fmt']}")
        crf = v["crf"]

        if v_codec == "libsvtav1":
            chunks = []
            if v["preset"]:
                chunks.append(f"preset={v['preset']}")
            if crf is not None:
                chunks.append(f"crf={crf}")
            if v["profile"]:
                chunks.append(f"profile={v['profile']}")
            if v["level"]:
                chunks.append(f"level={v['level'].replace('.', '')}")
            if v["extra_params"]:
                chunks.append(v["extra_params"])
            if chunks:
                args.append(f"-svtav1-params {':'.join(chunks)}")
        elif v_codec == "libx265":
            chunks = []
            if crf is not None:
                chunks.append(f"crf={crf}")
            if v["preset"]:
                chunks.append(f"preset={v['preset']}")
            if v["extra_params"]:
                chunks.append(v["extra_params"])
            if chunks:
                args.append(f"-x265-params {':'.join(chunks)}")
            args.append("-tag:v hvc1")
        else:
            if crf is not None:
                args.append(f"-crf {crf}")
            if v["preset"]:
                args.append(f"-preset {v['preset']}")

        # profile/level ride inside the codec params for SVT-AV1, and are
        # real flags everywhere else
        if v_codec != "libsvtav1":
            if v["profile"]:
                args.append(f"-profile:v {v['profile']}")
            if v["level"]:
                args.append(f"-level:v {v['level']}")

        for flag, key in (
            ("-color_primaries", "color_primaries"),
            ("-color_trc", "color_trc"),
            ("-colorspace", "colorspace"),
        ):
            if v[key]:
                args.append(f"{flag} {v[key]}")

        if scale := RESOLUTIONS.get(p["resolution"], ""):
            args.append(f"-vf scale={scale}")

    args.append(f"-c:a {a_codec}")
    if a_codec != "copy":
        if a["bitrate"]:
            args.append(f"-b:a {a['bitrate']}")
        if a["channels"]:
            args.append(f"-ac {a['channels']}")
        if a["vbr"] and a_codec in ("libopus", "aac"):
            args.append("-vbr on")

    if p["subtitle_mode"] == "copy":
        args.append("-c:s copy" if container != "mp4" else "-c:s mov_text")
    else:
        args.append("-sn")

    if container == "mkv":
        args.append("-c:t copy")

    for key, value in p["metadata"].items():
        if ":" in key:
            args.append(f'-metadata:{key} "{value}"')
        else:
            args.append(f'-metadata {key}="{value}"')

    for spec, value in p["disposition"].items():
        args.append(f"-disposition:{spec} {value}")

    if p["extra_args"]:
        args.append(p["extra_args"])

    args.append(f"mltb.{container}")
    if p["delete_original"]:
        args.append("-del")
    return " ".join(args)
