from falcon.asgi import Request, Response, WebSocket
from falcon.errors import WebSocketDisconnected, HTTPUnauthorized
from redis.asyncio import Redis
from msgspec.json import decode, encode
from msgspec import MsgspecError
from loguru import logger
from contextlib import suppress
from anonimus.server.struct import Message, Identify, On, Off, Element, Connection
from anonimus.server.api import get_chat_members, send_member_message


class Messanger:
    def __init__(self, redis: Redis, connections: dict[bytes, Connection[WebSocket]]) -> None:
        self._redis = redis
        self._connections = connections

    async def on_websocket(self, request: Request, websocket: WebSocket) -> None:
        uuid = request.cookies.get('uuid', '').encode()

        if not uuid:
            raise HTTPUnauthorized()

        try:
            await websocket.accept()
        except WebSocketDisconnected as error:
            raise error

        if uuid in self._connections:
            with suppress(OSError):
                await self._connections[uuid].socket.close()

        self._connections[uuid] = Connection(uuid, websocket, set())

        try:
            await self._process_websocket(self._connections[uuid], request)
        finally:
            with suppress(OSError):
                await self._connections[uuid].socket.close()

            del self._connections[uuid]

    async def _process_websocket(self, connection: Connection[WebSocket], request: Request) -> None:

        while connection.socket.ready:
            try:
                record = await connection.socket.receive_text()
            except WebSocketDisconnected as error:
                raise

            try:
                element = decode(record, type=Identify | Message | On)
            except MsgspecError as error:
                logger.error('Message decoding: %s' % error)
                continue

            try:
                await self._process_message(connection, element)
            except Exception as error:
                logger.error('Message processing: %s' % error)
                continue

    async def _process_message(self, connection: Connection, element: Element) -> None:
        match element:
            case On(name=name):
                connection.events.add(name)

            case Off(name=name):
                with suppress(KeyError):
                    connection.events.remove(name)

            case Message(text=text, chat=chat, uuid=uuid):
                for member in await get_chat_members(self._redis, chat):
                    await send_member_message(self._redis, member, {'uuid': str(uuid), 'text': text})


class People:
    def __init__(self, connections: dict[bytes, Connection]) -> None:
        self._connections = connections

    async def on_get(self, request: Request, response: Response) -> None:
        response.data = encode([connection.uuid for connection in self._connections.values()])


class Status:
    async def on_get(self, request: Request) -> None:
        pass
