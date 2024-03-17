from redis.asyncio import Redis
from redis.typing import KeyT, StreamIdT
from aiohttp.web_ws import WebSocketResponse
from aiohttp.web import AppKey
from msgspec import convert, to_builtins
from loguru import logger
from anonimus.server import struct
from anonimus.server.toolling.misc import repeat
from anonimus.server.struct import MessageResponse, EventReponse


REDIS = AppKey('redis', Redis)
CONNECTIONS = AppKey('connections', dict[str, struct.Connection[WebSocketResponse]])


@repeat(Exception, timeout=0, exception_timeout=2)
@logger.catch(message='Reading from "Redis" streams error', reraise=True)
async def read_redis(redis: Redis, connections: dict[str, struct.Connection[WebSocketResponse]]) -> None:
    if not connections:
        return

    streams: dict[KeyT, StreamIdT] = {
        k: v.context.get('ref') or '0-0' for k, v in connections.items()
    }

    for _stream, records in await redis.xread(streams=streams):
        stream = _stream.decode()

        try:
            connection = connections[stream]
        except KeyError:
            continue

        for _reference, _record in records:
            reference = _reference.decode()

            record = convert({
                k.decode(): v.decode() for k, v in _record.items()
            }, type=struct.Message | struct.Event, strict=False)

            match record:
                case struct.Message():
                    response = MessageResponse(message=record, reference=reference)
                case struct.Event():
                    response = EventReponse(event=record, reference=reference)

            try:
                await connection.socket.send_json(to_builtins(response))
            except Exception as error:
                continue

            connection.context['ref'] = reference


@repeat(Exception, timeout=3, exception_timeout=2)
@logger.catch(message='Cleaning from "Redis" error', reraise=True)
async def clear_redis(redis: Redis):
    pass
