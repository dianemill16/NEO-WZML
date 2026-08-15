# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)
#
# One long-lived Mongo client for the web process. Motor clients own a
# connection pool and a background monitor task, so creating one per
# request (as the first cut did) churns connections and leaks monitors
# under load — they are designed to be shared.

from bot.core.config_manager import Config

_client = None
_uri = None


def users_collection():
    """The same collection the bot writes user settings to, or None when
    no DATABASE_URL is configured."""
    global _client, _uri

    if not Config.DATABASE_URL:
        return None

    from motor.motor_asyncio import AsyncIOMotorClient

    # rebuild only if the URI actually changed (config can be edited live)
    if _client is None or _uri != Config.DATABASE_URL:
        if _client is not None:
            _client.close()
        _client = AsyncIOMotorClient(Config.DATABASE_URL)
        _uri = Config.DATABASE_URL

    bot_id = (Config.BOT_TOKEN or ":").split(":", 1)[0]
    if not bot_id:
        return None
    return _client.neowzml.users[bot_id]


async def load_db_config():
    """Pulls the current MongoDB-persisted config (the same values
    /bsetting writes and bot/core/startup.py loads for the main bot
    process) and applies it via Config.load_dict(). The web server runs
    as its own gunicorn process with its own Config.load() call (env vars
    / config.py only) — without this, anything changed through the bot's
    settings UI at runtime (BASE_URL included) never reaches this
    process, so it keeps using whatever value was baked in at container
    deploy time no matter what the operator sets later.

    Uses its own throwaway client rather than config_collection()'s
    shared one: this runs once at import time under a transient
    asyncio.run() loop, before uvicorn's real long-lived loop exists —
    caching a client bound to that transient loop would break every
    later request-time use of the shared client with a
    "attached to a different loop" error.
    """
    if not Config.DATABASE_URL:
        return
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(Config.DATABASE_URL)
    try:
        bot_id = (Config.BOT_TOKEN or ":").split(":", 1)[0]
        config_dict = await client.neowzml.settings.config.find_one(
            {"_id": bot_id}, {"_id": 0}
        )
        if config_dict:
            Config.load_dict(config_dict)
    finally:
        client.close()


def close():
    global _client, _uri
    if _client is not None:
        _client.close()
        _client = None
        _uri = None
