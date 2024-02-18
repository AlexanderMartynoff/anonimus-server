from redis.asyncio import Redis
from redis.typing import KeyT, StreamIdT
from aiohttp.web_ws import WebSocketResponse
from aiohttp.web import AppKey
from loguru import logger
from anonimus.server import struct
from anonimus.server.toolling.misc import repeat


REDIS = AppKey('redis', Redis)
CONNECTIONS = AppKey('connections', dict[str, struct.Connection[WebSocketResponse]])


@repeat(Exception, timeout=0, exception_timeout=2)
@logger.catch(message='Reading from "Redis" streams error', reraise=True)
async def read_redis(redis: Redis, connections: dict[str, struct.Connection[WebSocketResponse]]) -> None:
    if not connections:
        return

    streams: dict[KeyT, StreamIdT] = {
        k: connections[k].context.get('ref') or '0-0' for k in connections
    }

    for stream, messages in await redis.xread(streams=streams):
        uuid: str = stream.decode()

        if uuid not in connections:
            continue

        connection = connections[uuid]

        for id, message in messages:
            await connection.socket.send_json(
                {'id': id.decode()} | {k.decode(): v.decode() for k, v in message.items()}
            )
            connection.context['ref'] = id


@repeat(Exception, timeout=3, exception_timeout=2)
@logger.catch(message='Cleaning from "Redis" error', reraise=True)
async def clear_redis(redis: Redis):
    pass
