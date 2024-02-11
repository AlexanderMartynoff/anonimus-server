from typing import Any, Awaitable, Callable
import asyncio
from redis.asyncio import Redis
from redis.typing import KeyT, StreamIdT
from starlette.responses import Response
from starlette.websockets import WebSocket
from loguru import logger
from anonimus.server import struct


def repeat[T](function: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:

    async def repeater[**P](*args: P.args, **kwargs: P.kwargs) -> T:
        while True:
            try:
                await function(*args, **kwargs)
            except Exception as error:
                logger.error('When execute "%s": (%s) %s' % (function.__name__, error, error.__class__.__name__))

            await asyncio.sleep(0)

    return repeater


@repeat
async def read_redis(redis: Redis, connections: dict[str, struct.Connection[WebSocket]]) -> None:
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
async def clear_redis(redis: Redis):
    pass
