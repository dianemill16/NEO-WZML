#!/usr/bin/env python3
# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# NEO-WZML ULTRA theme — the chat counterpart of the ULTRA web UI.
# Framed section headers, a single ┃ gutter for every field and one
# consistent icon set, so bot replies read like the web panels.


class NeoStyle:

    ST_BN1_NAME = "⚡ GitHub"
    ST_BN1_URL = "https://github.com/irisXDR/NEO-WZML"
    ST_BN2_NAME = "◈ Channel"
    ST_BN2_URL = "https://t.me/Chiheisen"

    ST_MSG = """<blockquote><b>◈ NEO-WZML ULTRA</b></blockquote>
<i>Mirror & leech anything — torrents, direct links, Mega, Drive, yt-dlp —
to your cloud, to Telegram, or to a streaming link.</i>

┃ <b>Encoding profiles</b> · <code>/usetting</code>
┃ <b>Auto-rename</b> · <code>/autorename</code>
┃ <b>File to link</b> · <code>/link</code>

<b>Type {help_command} for the full command list.</b>"""

    ST_BOTPM = """<blockquote><b>◈ Connected</b></blockquote>
<i>All your files and links will arrive here. Start using the bot.</i>"""

    ST_UNAUTH = """<blockquote><b>◈ Connected</b></blockquote>
<i>All your files and links will arrive here. Start using the bot.</i>"""

    OWN_TOKEN_GENERATE = """<blockquote><b>✕ Token Not Yours</b></blockquote>
<i>Generate your own temporary token to continue.</i>"""

    USED_TOKEN = """<blockquote><b>✕ Token Already Used</b></blockquote>
<i>Generate a fresh one to continue.</i>"""

    LOGGED_PASSWORD = """<blockquote><b>✓ Already Logged In</b></blockquote>
<i>Logged in via password — temporary tokens aren't needed.</i>"""

    ACTIVATE_BUTTON = "⚡ Activate Token"

    TOKEN_MSG = """<blockquote><b>◈ Temporary Login Token</b></blockquote>
┃ <b>Token:</b> <code>{token}</code>
┃ <b>Validity:</b> {validity}"""

    ACTIVATED = "✅ Activated"
    LOGGED_IN = "<blockquote><b>✓ Already Logged In</b></blockquote>"
    INVALID_PASS = """<blockquote><b>✕ Invalid Password</b></blockquote>
<i>Check the password and try again.</i>"""
    PASS_LOGGED = """<blockquote><b>✓ Login Successful</b></blockquote>
<i>Permanent access granted.</i>"""
    LOGIN_USED = """<blockquote><b>◈ Login</b></blockquote>
┃ <b>Usage:</b> <code>/cmd [password]</code>"""

    LOG_DISPLAY_BT = "📑 Log Display"
    WEB_PASTE_BT = "📨 Web Paste"

    BASIC_BT = "◈ Basic"
    USER_BT = "◈ Users"
    MICS_BT = "◈ Misc"
    O_S_BT = "◈ Owner & Sudo"
    CLOSE_BT = "✕ Close"
    HELP_HEADER = """<blockquote><b>◈ HELP MENU</b></blockquote>
<i>Tap any command to see its details.</i>"""

    BOT_STATS = """<blockquote><b>◈ BOT STATISTICS</b></blockquote>
┃ <b>Uptime:</b> {bot_uptime}

<b>▰ MEMORY</b>
┃ {ram_bar} {ram}%
┃ <b>Used:</b> {ram_u} · <b>Free:</b> {ram_f} · <b>Total:</b> {ram_t}

<b>▰ SWAP</b>
┃ {swap_bar} {swap}%
┃ <b>Used:</b> {swap_u} · <b>Free:</b> {swap_f} · <b>Total:</b> {swap_t}

<b>▰ DISK</b>
┃ {disk_bar} {disk}%
┃ <b>Read:</b> {disk_read} · <b>Write:</b> {disk_write}
┃ <b>Used:</b> {disk_u} · <b>Free:</b> {disk_f} · <b>Total:</b> {disk_t}
"""

    SYS_STATS = """<blockquote><b>◈ SYSTEM</b></blockquote>
┃ <b>Uptime:</b> {os_uptime}
┃ <b>Version:</b> {os_version}
┃ <b>Arch:</b> {os_arch}

<blockquote><b>◈ NETWORK</b></blockquote>
┃ <b>Uploaded:</b> {up_data}
┃ <b>Downloaded:</b> {dl_data}
┃ <b>Packets:</b> ↑{pkt_sent}k · ↓{pkt_recv}k
┃ <b>Total I/O:</b> {tl_data}

<blockquote><b>◈ CPU</b></blockquote>
┃ {cpu_bar} {cpu}%
┃ <b>Frequency:</b> {cpu_freq}
┃ <b>Avg Load:</b> {sys_load}
┃ <b>Cores:</b> {p_core}P · {v_core}V · {total_core} total
┃ <b>Usable:</b> {cpu_use}
"""

    REPO_STATS = """<blockquote><b>◈ REPOSITORY</b></blockquote>
┃ <b>Updated:</b> {last_commit}
┃ <b>Version:</b> {bot_version}
┃ <b>Latest:</b> {lat_version}
┃ <b>Changelog:</b> {commit_details}

✦ <b>Remarks:</b> <code>{remarks}</code>
"""

    BOT_LIMITS = """<blockquote><b>◈ LIMITS</b></blockquote>
┃ <b>Direct:</b> {DL} GB · <b>Torrent:</b> {TL} GB
┃ <b>GDrive:</b> {GL} GB · <b>RClone:</b> {RL} GB
┃ <b>YT-DLP:</b> {YL} GB · <b>Playlist:</b> {PL}
┃ <b>Mega:</b> {ML} GB · <b>Clone:</b> {CL} GB
┃ <b>Leech:</b> {LL} GB · <b>JDown:</b> {JL} GB
┃ <b>Archive:</b> {AL} GB · <b>Extract:</b> {EL} GB
┃ <b>Storage Threshold:</b> {TS} GB
"""

    RESTARTING = "<i>◈ Restarting…</i>"
    RESTART_SUCCESS = """<blockquote><b>✓ RESTARTED</b></blockquote>
┃ <b>Date:</b> {date}
┃ <b>Time:</b> {time} ({timz})
┃ <b>Version:</b> {version}"""
    RESTARTED = """<blockquote><b>✓ BOT RESTARTED</b></blockquote>
┃ <b>Date:</b> {date}
┃ <b>Time:</b> {time} ({timz})
┃ <b>Version:</b> {version}"""

    PING = "<i>◈ Pinging…</i>"
    PING_VALUE = """<blockquote><b>◈ PONG</b></blockquote>
┃ <code>{value} ms</code>"""

    PM_START = """<blockquote><b>◈ TASK STARTED</b></blockquote>
┃ <b>Source:</b> <a href='{msg_link}'>Click Here</a>"""

    L_LOG_START = """<blockquote><b>◈ LEECH STARTED</b></blockquote>
┃ <b>User:</b> {mention} (#ID{uid})
┃ <b>Source:</b> <a href='{msg_link}'>Click Here</a>"""

    LINKS_START = """<blockquote><b>◈ TASK STARTED</b></blockquote>
┃ <b>Mode:</b> {Mode}
┃ <b>By:</b> {Tag}\n\n"""

    LINKS_SOURCE = """<b>▰ Source</b>
┃ <b>Added:</b> {On}
━━━━━━━━━━━━━━━━━━━━
{Source}
━━━━━━━━━━━━━━━━━━━━\n\n"""

    NAME = "<blockquote><b>◈ {Name}</b></blockquote>\n\n"
    SIZE = "┃ <b>Size:</b> {Size}\n"
    ELAPSE = "┃ <b>Elapsed:</b> {Time}\n"
    MODE = "┃ <b>Mode:</b> {Mode}\n"

    L_TOTAL_FILES = "┃ <b>Total Files:</b> {Files}\n"
    L_CORRUPTED_FILES = "┃ <b>Corrupted:</b> {Corrupt}\n"
    L_CC = "┃ <b>By:</b> {Tag}\n\n"
    PM_BOT_MSG = "✦ <i>File(s) sent above.</i>"
    L_BOT_MSG = "✦ <i>File(s) sent to your Bot PM.</i>"
    L_LL_MSG = "✦ <i>File(s) sent — access them via the links below.</i>\n"

    M_TYPE = "┃ <b>Type:</b> {Mimetype}\n"
    M_SUBFOLD = "┃ <b>SubFolders:</b> {Folder}\n"
    TOTAL_FILES = "┃ <b>Files:</b> {Files}\n"
    RCPATH = "┃ <b>Path:</b> <code>{RCpath}</code>\n"
    M_CC = "┃ <b>By:</b> {Tag}\n\n"
    M_BOT_MSG = "✦ <i>Link(s) sent to your Bot PM.</i>"

    CLOUD_LINK = "☁️ Cloud"
    SAVE_MSG = "📨 Save"
    RCLONE_LINK = "☁️ RClone"
    DDL_LINK = "📎 {Serv}"
    SOURCE_URL = "🔐 Source"
    INDEX_LINK_F = "🗂 Index"
    INDEX_LINK_D = "⚡ Index"
    VIEW_LINK = "🌐 View"
    CHECK_PM = "📥 Bot PM"
    CHECK_LL = "🖇 Links Log"
    MEDIAINFO_LINK = "📃 MediaInfo"
    SCREENSHOTS = "🖼 Screenshots"

    STATUS_NAME = "<b>{TaskNum}. <i>{Name}</i></b>"

    BAR = "\n┃ {Bar}"
    PROCESSED = "\n┃ <b>Done:</b> {Processed}"
    STATUS = '\n┃ <b>Status:</b> <a href="{Url}">{Status}</a>'
    ETA = "\n┃ <b>ETA:</b> {Eta}"
    SPEED = "\n┃ <b>Speed:</b> {Speed}"
    ELAPSED = "\n┃ <b>Elapsed:</b> {Elapsed}"
    ENGINE = "\n┃ <b>Engine:</b> {Engine}"
    STA_MODE = "\n┃ <b>Mode:</b> {Mode}"
    SEEDERS = "\n┃ <b>Seeders:</b> {Seeders} · "
    LEECHERS = "<b>Leechers:</b> {Leechers}"
    FILES_PROGRESS = "\n┃ <b>Files:</b> {Files}"

    SEED_SIZE = "\n┃ <b>Size:</b> {Size}"
    SEED_SPEED = "\n┃ <b>Speed:</b> {Speed} · "
    UPLOADED = "<b>Uploaded:</b> {Upload}"
    RATIO = "\n┃ <b>Ratio:</b> {Ratio} · "
    TIME = "<b>Time:</b> {Time}"
    SEED_ENGINE = "\n┃ <b>Engine:</b> {Engine}"

    STATUS_SIZE = "\n┃ <b>Size:</b> {Size}"
    NON_ENGINE = "\n┃ <b>Engine:</b> {Engine}"

    USER = "\n┃ <b>User:</b> <code>{User}</code>"
    ID = "\n┃ <b>User ID:</b> <code>{Id}</code>"
    BTSEL = "\n┃ <b>Select:</b> {Btsel}"
    CANCEL = "\n┃ {Cancel}\n\n"

    FOOTER = "<blockquote><b>◈ BOT STATS</b></blockquote>\n"
    TASKS = "┃ <b>Tasks:</b> {Tasks}\n"
    BOT_TASKS = "┃ <b>Tasks:</b> {Tasks}/{Ttask} · <b>Free:</b> {Free}\n"
    Cpu = "┃ <b>CPU:</b> {cpu}% · "
    FREE = "<b>Disk:</b> {free} [{free_p}%]"
    Ram = "\n┃ <b>RAM:</b> {ram}% · "
    uptime = "<b>Uptime:</b> {uptime}"
    DL = "\n┃ <b>↓</b> {DL}/s · "
    UL = "<b>↑</b> {UL}/s"

    PREVIOUS = "❮"
    REFRESH = "◈ {Page}"
    NEXT = "❯"

    STOP_DUPLICATE = """<blockquote><b>✕ DUPLICATE</b></blockquote>
<i>Already available in Drive. Matching results:</i> {content}"""

    COUNT_MSG = """<blockquote><b>◈ COUNTING</b></blockquote>
┃ <code>{LINK}</code>"""
    COUNT_NAME = "<blockquote><b>◈ {COUNT_NAME}</b></blockquote>\n\n"
    COUNT_SIZE = "┃ <b>Size:</b> {COUNT_SIZE}\n"
    COUNT_TYPE = "┃ <b>Type:</b> {COUNT_TYPE}\n"
    COUNT_SUB = "┃ <b>SubFolders:</b> {COUNT_SUB}\n"
    COUNT_FILE = "┃ <b>Files:</b> {COUNT_FILE}\n"
    COUNT_CC = "┃ <b>By:</b> {COUNT_CC}\n"

    LIST_SEARCHING = "<i>◈ Searching for <b>{NAME}</b>…</i>"
    LIST_FOUND = "<blockquote><b>◈ {NO} result(s) for {NAME}</b></blockquote>"
    LIST_NOT_FOUND = "<i>✕ No results for <b>{NAME}</b></i>"

    NO_ACTIVE_DL = """<blockquote><b>◈ IDLE</b></blockquote>
<i>No active downloads.</i>

<blockquote><b>◈ BOT STATS</b></blockquote>
┃ <b>CPU:</b> {cpu}% · <b>Disk:</b> {free} [{free_p}%]
┃ <b>RAM:</b> {ram} · <b>Uptime:</b> {uptime}
"""

    USER_SETTING = """<blockquote><b>◈ USER SETTINGS</b></blockquote>
┃ <b>Name:</b> {NAME} (<code>{ID}</code>)
┃ <b>Username:</b> {USERNAME}
┃ <b>Telegram DC:</b> {DC}"""

    UNIVERSAL = """<blockquote><b>◈ UNIVERSAL · {NAME}</b></blockquote>
┃ <b>YT-DLP Options:</b> <code>{YT}</code>
┃ <b>Daily Tasks:</b> <code>{DT}</code> per day
┃ <b>Last Bot Used:</b> <code>{LAST_USED}</code>
┃ <b>User Session:</b> <code>{USESS}</code>
┃ <b>MediaInfo:</b> <code>{MEDIAINFO}</code>
┃ <b>Save Mode:</b> <code>{SAVE_MODE}</code>
┃ <b>Bot PM:</b> <code>{BOT_PM}</code>"""

    MIRROR = """<blockquote><b>◈ MIRROR / CLONE · {NAME}</b></blockquote>
┃ <b>RClone Config:</b> <i>{RCLONE}</i>
┃ <b>Prefix:</b> <code>{MPREFIX}</code>
┃ <b>Suffix:</b> <code>{MSUFFIX}</code>
┃ <b>Name Swap:</b> <code>{MREMNAME}</code>
┃ <b>DDL Server(s):</b> <i>{DDL_SERVER}</i>
┃ <b>User TD Mode:</b> <i>{TMODE}</i>
┃ <b>Total User TD(s):</b> <i>{USERTD}</i>
┃ <b>Daily Mirror:</b> <code>{DM}</code> per day"""

    LEECH = """<blockquote><b>◈ LEECH · {NAME}</b></blockquote>
┃ <b>Daily Leech:</b> <code>{DL}</code> per day
┃ <b>Leech Type:</b> <i>{LTYPE}</i>
┃ <b>Thumbnail:</b> <i>{THUMB}</i>
┃ <b>Equal Splits:</b> <i>{EQUAL_SPLIT}</i>
┃ <b>Caption:</b> <code>{LCAPTION}</code>
┃ <b>Prefix:</b> <code>{LPREFIX}</code>
┃ <b>Suffix:</b> <code>{LSUFFIX}</code>
┃ <b>Caption Style:</b> <i>{LCAPTIONSTYLE}</i>
┃ <b>Dumps:</b> <code>{LDUMP}</code>
┃ <b>Name Swap:</b> <code>{LREMNAME}</code>
┃ <b>Metadata:</b> <code>{LMETA}</code>"""
