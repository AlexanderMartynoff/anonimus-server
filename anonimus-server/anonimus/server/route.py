from __future__ import annotations
from aiohttp import web


routes = web.RouteTableDef()


@routes.get('/')
async def index(request) -> web.Response:
    return web.Response()


@routes.post('/message/send')
async def send_message(request) -> web.Response:
    return web.Response()


@routes.put('/session/close')
async def close_session(request) -> web.Response:
    return web.Response()
