from falcon.asgi import Request, Response, WebSocket
from falcon.errors import WebSocketDisconnected, HTTPForbidden
from redis.asyncio import Redis
from redis.exceptions import RedisError
from msgspec.json import decode, encode
from msgspec import MsgspecError
from loguru import logger
from contextlib import suppress
from anonimus.server.struct import Message, On, Off, Element, Connection
from anonimus.server.api import find_chat_members, put_message


class Messanger:
    def __init__(self, redis: Redis, connections: dict[str, Connection[WebSocket]]) -> None:
        self._redis = redis
        self._connections = connections

    async def on_websocket(self, request: Request, websocket: WebSocket) -> None:
        uuid: str = request.cookies.get('uuid')  # type: ignore

        if not uuid:
            raise HTTPForbidden()

        if uuid in self._connections:
            raise HTTPForbidden()

        try:
            await websocket.accept()
        except WebSocketDisconnected as error:
            raise error

        self._connections[uuid] = Connection(uuid, websocket, {
            'ref': request.get_param('ref', default='0-0'),  # type: ignore
        })

        with suppress(RedisError):
            await self._on_connection_change()

        try:
            await self._process_connection(self._connections[uuid], request)
        finally:
            try:
                await websocket.close()
            finally:
                with suppress(KeyError):
                    del self._connections[uuid]

                with suppress(RedisError):
                    await self._on_connection_change()

    async def _process_connection(self, connection: Connection[WebSocket], request: Request) -> None:
        while connection.socket.ready:
            record = await connection.socket.receive_text()

            try:
                element = decode(record, type=On | Off | Message)
            except MsgspecError as error:
                logger.error('Message decoding: %s' % error)
                continue

            try:
                await self._process_message(connection, element)
            except Exception as error:
                logger.error('Message processing: %s' % error)

    async def _process_message(self, connection: Connection[WebSocket], element: Element) -> None:
        match element:
            case On(name=name):
                connection.streams.add(name)

            case Off(name=name):
                with suppress(KeyError):
                    connection.streams.remove(name)

            case Message(text=text, chat=chat, uuid=uuid, sender=sender):
                for member in await find_chat_members(self._redis, chat):
                    await put_message(self._redis, member, {'type': 'Message', 'uuid': str(uuid), 'text': text, 'sender': sender})

    async def _on_connection_change(self):
        for connection in self._connections.values():
            await put_message(self._redis, connection.uuid, {'type': 'Online'})


class WhoOnline:
    def __init__(self, connections: dict[str, Connection]) -> None:
        self._connections = connections

    async def on_get(self, request: Request, response: Response) -> None:
        response.data = encode([uuid for uuid in self._connections])


class Status:
    async def on_get(self, request: Request) -> None:
        pass
