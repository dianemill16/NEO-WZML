# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# Google Drive token.pickle generator. Runs the OAuth consent flow in the
# browser and stores the resulting credentials as the user's TOKEN_PICKLE
# (tokens/<user_id>.pickle + the same field in Mongo), which is exactly
# what the Drive helper already reads.

from logging import getLogger
from os import makedirs, path as ospath
from pickle import dumps as pickle_dumps

from bot.core.config_manager import Config

LOGGER = getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "credentials.json"
PURPOSE = "google-token"


def credentials_available():
    return ospath.exists(CREDENTIALS_FILE)


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

    if not Config.DATABASE_URL:
        return path

    from motor.motor_asyncio import AsyncIOMotorClient

    bot_id = (Config.BOT_TOKEN or ":").split(":", 1)[0]
    client = AsyncIOMotorClient(Config.DATABASE_URL)
    try:
        await client.neowzml.users[bot_id].update_one(
            {"_id": user_id}, {"$set": {"TOKEN_PICKLE": token_bytes}}, upsert=True
        )
    finally:
        client.close()
    return path
