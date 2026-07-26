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


def close():
    global _client, _uri
    if _client is not None:
        _client.close()
        _client = None
        _uri = None
