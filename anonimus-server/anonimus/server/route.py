from __future__ import annotations
from aiohttp.web import WebSocketResponse, RouteTableDef, Request, AppKey
from aiohttp import WSMsgType
from msgspec.json import decode
from .struct import Message, Identity, Element, Status
from .api import Redis, Db
from . import service


routes = RouteTableDef()


@routes.get('/api/messanger/connect')
async def connect(request: Request) -> WebSocketResponse:
    stream = WebSocketResponse()

    await stream.prepare(request)

    async for msg in stream:
        if msg.type == WSMsgType.text:
            print(msg.data)
            try:
                element = decode(msg.data, type=Identity | Message | Status)
            except TypeError:
                raise

            match element:
                case Identity():
                    pass
                case Status():
                    pass
                case Message():
                    pass

        if msg.type == WSMsgType.error:
            continue

    return stream
