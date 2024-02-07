from asyncio import ensure_future
from falcon.asgi import Request, Response, WebSocket
from falcon.errors import WebSocketDisconnected, HTTPUnauthorized
from redis.asyncio import Redis
from msgspec.json import decode, encode
from msgspec import MsgspecError
from loguru import logger
from contextlib import suppress
from anonimus.server.struct import Message, Identify, On, Off, Element, Connection, ConnectionManager
from anonimus.server.api import get_chat_members, put_message


class Messanger:
    def __init__(self, redis: Redis, manager: ConnectionManager[WebSocket]) -> None:
        self._redis = redis
        self._manager = manager

    async def on_websocket(self, request: Request, websocket: WebSocket) -> None:
        uuid: str = request.cookies.get('uuid')  # type: ignore
        start_message_id: str = request.get_param('last_message_id', '0')  # type: ignore

        if not uuid:
            raise HTTPUnauthorized()

        try:
            await websocket.accept()
        except WebSocketDisconnected as error:
            raise error

        if uuid in self._manager:
            with suppress(OSError):
                await self._manager.close(uuid)

        self._connections[uuid] = Connection(uuid, websocket, {
            'start_message_id': start_message_id,
        })

        try:
            await self._process_connection(self._connections[uuid], request)
        finally:
            with suppress(OSError):
                await self._connections[uuid].socket.close()

            del self._connections[uuid]

    async def _process_connection(self, connection: Connection[WebSocket], request: Request) -> None:
        # Each user has personal redis stream (mainbox) by name `uuid`
        connection.streams.add(connection.uuid)

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

    async def _process_message(self, connection: Connection[WebSocket], element: Element) -> None:
        match element:
            case On(name=name):
                connection.streams.add(name)

            case Off(name=name):
                with suppress(KeyError):
                    connection.streams.remove(name)

            case Message(text=text, chat=chat, uuid=uuid):
                for member in await get_chat_members(self._redis, chat):
                    await put_message(self._redis, member, {'type': 'Message', 'uuid': str(uuid), 'text': text})

    async def _put_message_online(self):
        for uuid in self._connections:
            await put_message(self._redis, uuid, {'type': 'Online'})


class People:
    def __init__(self, connections: dict[str, Connection]) -> None:
        self._connections = connections

    async def on_get(self, request: Request, response: Response) -> None:
        response.data = encode([connection.uuid for connection in self._connections.values()])


class Status:
    async def on_get(self, request: Request) -> None:
        pass
