from falcon.asgi import Request, Response, WebSocket
from falcon.errors import WebSocketDisconnected
from redis.asyncio import Redis
from msgspec.json import decode, encode
from msgspec import MsgspecError
from loguru import logger
from anonimus.server.struct import Message, Identify, On, Element, Connection


class Messanger:
    def __init__(self, redis: Redis, connections: dict[WebSocket, Connection]) -> None:
        self._redis = redis
        self._connections = connections

    async def on_websocket(self, request: Request, websocket: WebSocket) -> None:
        try:
            await websocket.accept()
        except WebSocketDisconnected as error:
            return

        self._connections[websocket] = Connection()

        while True:
            try:
                record = await websocket.receive_text()
            except WebSocketDisconnected as error:
                raise

            try:
                element = decode(record, type=Identify | Message | On)
            except MsgspecError as error:
                logger.error('Message decoding: %s' % error)
                continue

            try:
                await self._process(websocket, element)
            except Exception as error:
                logger.error('Message processing: %s' % error)
                continue

    async def _process(self, websocket: WebSocket, element: Element) -> None:
        user = self._connections[websocket]

        match element:
            case Identify(name=name):
                user.name = name
            case On(name=name):
                pass
            case Message(text=text, receiver=receiver):
                await self._send(user.name, receiver, text)

    async def _send(self, sender, receiver, text) -> None:
        async with self._redis as redis:
            await redis.xadd(f'{sender}->receiver', {'text': text})


class Contact:
    def __init__(self, connections: dict[WebSocket, Connection]) -> None:
        self._connections = connections

    async def on_get(self, request: Request, response: Response) -> None:
        response.data = encode([user for user in self._connections.values()])


class Status:
    async def on_get(self, request: Request) -> None:
        pass
