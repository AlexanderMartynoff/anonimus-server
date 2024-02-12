from typing import Any, Awaitable, Callable
import asyncio
from redis.asyncio import Redis
from redis.typing import KeyT, StreamIdT
from aiohttp.web_ws import WebSocketResponse
from aiohttp.web import AppKey
from loguru import logger
from anonimus.server import struct
from anonimus.server.toolling.misc import repeat


REDIS = AppKey('redis', Redis)
CONNECTIONS = AppKey('users', dict[str, struct.Connection[WebSocketResponse]])


@repeat
@logger.catch(Exception, message='Reading from "Redis" streams error')
async def read_redis(redis: Redis, connections: dict[str, struct.Connection[WebSocketResponse]]) -> None:
    if not connections:
        return

    streams: dict[KeyT, StreamIdT] = {
        k: connections[k].context.get('ref') or '0-0' for k in connections
    }

    for stream, record in await redis.xread(streams=streams):
        uuid: str = stream.decode()

        if uuid not in connections:
            continue

        connection = connections[uuid]

        for id, message in record:
            await connection.socket.send_json(
                {'id': id.decode()} | {k.decode(): v.decode() for k, v in message.items()}
            )
            connection.context['ref'] = id


@repeat
@logger.catch(Exception, message='Cleaning from "Redis" error')
async def clear_redis(redis: Redis):
    pass
