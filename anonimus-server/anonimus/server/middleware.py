from typing import Any, Awaitable, Callable
import asyncio
from redis.asyncio import Redis
from redis.typing import KeyT, StreamIdT
from falcon.asgi import WebSocket
from loguru import logger
from anonimus.server import struct


class BackgroundWorker:
    def __init__(self, redis: Redis, connections: dict[bytes, struct.Connection[WebSocket]]):
        self._redis = redis
        self._connections = connections
        self._futures: list[asyncio.Future[Any]] = []

    async def process_startup(self, scope, event):
        self._start([
            self._process_garbage,
            self._process_mailboxes,
        ])

    async def process_shutdown(self, scope, event):
        self._stop()

    def _start(self, functions: list[Callable[[], Awaitable[None]]]):
        for function in functions:
            self._futures.append(asyncio.ensure_future(self._repeat(function)))

    def _stop(self):
        for future in self._futures:
            future.cancel()

        self._futures.clear()

    async def _repeat(self, function: Callable[[], Awaitable[None]]):
        while True:
            try:
                await function()
            except Exception as error:
                logger.error('When execute "%s": %s' % (function.__name__, error))

            await asyncio.sleep(0)

    async def _process_mailboxes(self) -> None:
        if not self._connections:
            return

        streams: dict[KeyT, StreamIdT] = {uuid: '$' for uuid in self._connections}

        for stream, record in await self._redis.xread(streams=streams, block=3000):
            if stream not in self._connections:
                continue

            connection = self._connections[stream]

            for _, message in record:
                await connection.socket.send_media(
                    {'type': 'Message'} | {k.decode(): v.decode() for k, v in message.items()}
                )

    async def _process_garbage(self) -> None:
        pass
