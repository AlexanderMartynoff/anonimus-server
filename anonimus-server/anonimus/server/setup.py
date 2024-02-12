from contextlib import suppress
from aiohttp import web
from aiojobs.aiohttp import AIOJOBS_SCHEDULER
from anonimus.server.service import REDIS, CONNECTIONS
from redis.asyncio import Redis, RedisError
from anonimus.server.service import read_redis, clear_redis


async def cleanup_context(app: web.Application):
    ''' Setup/Teardown services
    '''

    app[REDIS] = redis = Redis(host='localhost', port=6379, max_connections=10)
    app[CONNECTIONS] = connections = {}

    await app[AIOJOBS_SCHEDULER].spawn(read_redis(redis, connections))
    await app[AIOJOBS_SCHEDULER].spawn(clear_redis(redis))

    yield

    with suppress(RedisError):
        await redis.aclose()

    connections.clear()
