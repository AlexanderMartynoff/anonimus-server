from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import JSONResponse
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocket, WebSocketState
from starlette.requests import Request
from redis.asyncio import Redis
from redis.exceptions import RedisError
from msgspec.json import decode, encode
from msgspec import MsgspecError
from loguru import logger
from contextlib import suppress
from anonimus.server.struct import Message, On, Off, Element, Connection
from anonimus.server.api import find_chat_members, put_message


class Messanger(WebSocketEndpoint):
    connections: dict[str, Connection]
    redis: Redis

    async def on_connect(self, websocket: WebSocket) -> None:
        """Override to handle an incoming websocket connection"""
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket) -> None:
        uuid: str | None = websocket.cookies.get('uuid')

        if not uuid:
            raise ValueError()

        if uuid in self.connections:
            raise ValueError()

        self.connections[uuid] = Connection(uuid, websocket, {
            'ref': websocket.query_params.get('ref'),
        })

        with suppress(RedisError):
            await self._on_connection_change()

        try:
            await self._process_connection(self.connections[uuid])
        finally:
            try:
                await websocket.close()
            finally:
                with suppress(KeyError):
                    del self.connections[uuid]

                with suppress(RedisError):
                    await self._on_connection_change()

    async def _process_connection(self, connection: Connection[WebSocket]) -> None:
        while connection.socket.client_state == WebSocketState.CONNECTED:
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
                for member in await find_chat_members(self.redis, chat):
                    await put_message(self.redis, member, {'type': 'Message', 'uuid': str(uuid), 'text': text, 'sender': sender})


    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self._on_connection_change()

    async def _on_connection_change(self) -> None:
        for connection in self.connections.values():
            await put_message(self.redis, connection.uuid, {'type': 'Online'})


class WhoOnline(HTTPEndpoint):
    connections: dict[str, Connection[WebSocket]]

    async def get(self, request: Request) -> JSONResponse:
        return JSONResponse([uuid for uuid in self.connections])


class Status(HTTPEndpoint):
    connections: dict[str, Connection[WebSocket]]

    async def get(self, request: Request) -> None:
        pass
