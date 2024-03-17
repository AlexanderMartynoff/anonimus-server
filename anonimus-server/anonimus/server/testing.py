from typing import Any
from aiohttp import web
from fakeredis.aioredis import FakeRedis
from anonimus.server.worker import REDIS
from anonimus.server.setup import setup_connections, setup_aiojobs_scheduler, setup_routes


def setup_redis(app: web.Application):
    async def cleanup_context(app: web.Application):
        app[REDIS] = redis = FakeRedis()

        yield

        await redis.flushall()

    app.cleanup_ctx.append(cleanup_context)


def create_app(config: dict[str, Any] | None = None):
    app = web.Application()

    setup_routes(app)
    setup_redis(app)
    setup_connections(app)
    setup_aiojobs_scheduler(app)

    return app
