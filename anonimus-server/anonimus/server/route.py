from __future__ import annotations
from aiohttp.web import Response, WebSocketResponse, RouteTableDef, Request, json_response
from aiohttp import WSMsgType
from msgspec.json import decode
import loguru
from .struct import Message, Registration, Status, Subscription, Ping
from .service import Key


routes = RouteTableDef()


@routes.get('/api/messanger/connect')
async def connection(request: Request) -> WebSocketResponse:
    socket = WebSocketResponse()

    await socket.prepare(request)

    async for msg in socket:
        if msg.type == WSMsgType.text:
            try:
                element = decode(msg.data, type=Registration | Message | Status | Subscription | Ping)
            except TypeError:
                raise

            match element:
                case Registration(sender=sender):
                    request.app[Key.socket].add(socket)
                case Status(value=value):
                    pass
                case Subscription():
                    async with request.app[Key.redis] as redis:
                        length = await redis.xlen('user')

                        print('length', length)
                case Message(text=text):
                    async with request.app[Key.redis] as redis:
                        id = await redis.xadd('user', {'text': text})

                        print('id', id)

        if msg.type == WSMsgType.error:
            continue

    return socket
