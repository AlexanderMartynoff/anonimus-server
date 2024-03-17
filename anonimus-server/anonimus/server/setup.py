from typing import Any
from contextlib import suppress
from aiohttp import web
from aiojobs.aiohttp import AIOJOBS_SCHEDULER, setup as aiojobs_setup
from anonimus.server.worker import REDIS, CONNECTIONS
from redis.asyncio import Redis, RedisError
from anonimus.server.worker import read_redis, clear_redis
from anonimus.server import view


def setup_aiojobs_scheduler(app: web.Application):
    aiojobs_setup(app)

    async def cleanup_context(app: web.Application):
        await app[AIOJOBS_SCHEDULER].spawn(read_redis(app[REDIS], app[CONNECTIONS]))
        await app[AIOJOBS_SCHEDULER].spawn(clear_redis(app[REDIS]))

        yield

    app.cleanup_ctx.append(cleanup_context)


def setup_redis(app: web.Application):
    async def cleanup_context(app: web.Application):
        app[REDIS] = redis = Redis(host='localhost', port=6379, max_connections=10)

        yield

        with suppress(RedisError):
            await redis.aclose()

    app.cleanup_ctx.append(cleanup_context)


def setup_connections(app: web.Application):
    async def cleanup_context(app: web.Application):
        app[CONNECTIONS] = connections = {}

        yield

        connections.clear()

    app.cleanup_ctx.append(cleanup_context)


def setup_routes(app: web.Application):
    app.router.add_view('/api/messanger/connect', view.MessangerView)
    app.router.add_view('/api/online-user', view.OnlineUserView)
