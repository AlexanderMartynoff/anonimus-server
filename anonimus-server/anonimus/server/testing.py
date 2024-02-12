from typing import Callable, AsyncIterable
from contextlib import suppress
from aiohttp import web
from aiojobs.aiohttp import AIOJOBS_SCHEDULER
from anonimus.server.service import REDIS, CONNECTIONS
from redis.asyncio import Redis, RedisError
from anonimus.server.service import read_redis, clear_redis
from anonimus.server.struct import Connection


async def cleanup_context_factory(
        redis: Redis,
        connections: dict[str, Connection[web.WebSocketResponse]]) -> Callable[[web.Application], AsyncIterable[None]]:

    async def cleanup_context(app: web.Application) -> AsyncIterable[None]:
        app[REDIS] = redis
        app[CONNECTIONS] = connections

        await app[AIOJOBS_SCHEDULER].spawn(read_redis(redis, connections))
        await app[AIOJOBS_SCHEDULER].spawn(clear_redis(redis))

        yield

        with suppress(RedisError):
            await redis.aclose()

        connections.clear()

    return cleanup_context
