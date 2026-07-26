# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# Google Drive token.pickle generator. Runs the OAuth consent flow in the
# browser and stores the resulting credentials as the user's TOKEN_PICKLE
# (tokens/<user_id>.pickle + the same field in Mongo), which is exactly
# what the Drive helper already reads.

from json import dumps as json_dumps, loads as json_loads
from logging import getLogger
from os import makedirs, path as ospath
from pickle import dumps as pickle_dumps

from bot.core.config_manager import Config

LOGGER = getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "credentials.json"
PURPOSE = "google-token"


def ensure_credentials_file():
    """Create credentials.json from config when it's missing.

    Google's client_id/client_secret can only come from the owner's Google
    Cloud project, so this can't invent working credentials — it just
    saves the owner from having to upload a file through Telegram (which
    rejects .json on some clients). Supply either GOOGLE_CREDENTIALS_JSON
    (the whole file pasted in) or GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET.
    Returns True when a usable file exists afterwards.
    """
    if ospath.exists(CREDENTIALS_FILE):
        return True

    raw = (getattr(Config, "GOOGLE_CREDENTIALS_JSON", "") or "").strip()
    if raw:
        try:
            parsed = json_loads(raw)
        except ValueError as e:
            LOGGER.error(f"GOOGLE_CREDENTIALS_JSON is not valid JSON: {e}")
            return False
        if not isinstance(parsed, dict) or not (
            parsed.get("web") or parsed.get("installed")
        ):
            LOGGER.error(
                "GOOGLE_CREDENTIALS_JSON must be the OAuth client file "
                "containing a 'web' or 'installed' section."
            )
            return False
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(json_dumps(parsed, indent=2))
        LOGGER.info("Created credentials.json from GOOGLE_CREDENTIALS_JSON")
        return True

    client_id = (getattr(Config, "GOOGLE_CLIENT_ID", "") or "").strip()
    client_secret = (getattr(Config, "GOOGLE_CLIENT_SECRET", "") or "").strip()
    if not (client_id and client_secret):
        return False

    payload = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "project_id": client_id.split("-", 1)[0] or "neo-wzml",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [_redirect_uri()],
        }
    }
    with open(CREDENTIALS_FILE, "w") as f:
        f.write(json_dumps(payload, indent=2))
    LOGGER.info(
        "Created credentials.json from GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET"
    )
    return True


def credentials_available():
    return ensure_credentials_file()


def _redirect_uri():
    base = (Config.BASE_URL or "").rstrip("/")
    return f"{base}/app/token-generator/callback"


def build_flow(state=None):
    """OAuth flow configured for our web callback."""
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=_redirect_uri(),
        state=state,
    )
    return flow


def authorization_url(state):
    flow = build_flow(state)
    url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",  # force a refresh_token even on re-auth
        include_granted_scopes="true",
    )
    return url


def exchange_code(code, state):
    """Swap the OAuth code for credentials; returns the pickled bytes."""
    flow = build_flow(state)
    flow.fetch_token(code=code)
    creds = flow.credentials
    if not creds or not creds.refresh_token:
        raise ValueError(
            "Google returned no refresh token — revoke the app's access and retry."
        )
    return pickle_dumps(creds)


async def store_token(user_id, token_bytes):
    """Persist to disk and Mongo the same way user settings does."""
    makedirs("tokens", exist_ok=True)
    path = f"tokens/{user_id}.pickle"
    with open(path, "wb") as f:
        f.write(token_bytes)

    from web.mongo import users_collection

    coll = users_collection()
    if coll is None:
        return path
    await coll.update_one(
        {"_id": user_id}, {"$set": {"TOKEN_PICKLE": token_bytes}}, upsert=True
    )
    return path
