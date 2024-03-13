import asyncio
from collections import defaultdict
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

    decoders = defaultdict(
        lambda: lambda v: v.decode(),
        sequence=int,
        time=int,
    )

    for stream, records in await redis.xread(streams=streams):
        connection = connections.get(stream.decode())

        if not connection:
            continue

        for ref, record in records:
            reference = ref.decode()

            message = {}

            for k, v in record.items():
                key = k.decode()
                value = decoders[key](v)

                message[key] = value

            asyncio.ensure_future(connection.socket.send_json(message | {'ref': reference}))

            connection.context['ref'] = reference


@repeat(Exception, timeout=3, exception_timeout=2)
@logger.catch(message='Cleaning from "Redis" error', reraise=True)
async def clear_redis(redis: Redis):
    pass
