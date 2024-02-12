from typing import Callable, Union, Awaitable
from asyncio import sleep
from aiohttp import web
from aiohttp.test_utils import TestClient, BaseTestServer
from pytest_aiohttp.plugin import AiohttpClient
from redis.asyncio import Redis
from anonimus.server.view import MessangerView, ConnectionView
from anonimus.server.setup import cleanup_context
from aiojobs.aiohttp import setup as aiojobs_setup


async def test_websocket(aiohttp_client: Callable[..., Awaitable[TestClient]]):
    app = web.Application()

    aiojobs_setup(app)

    app.cleanup_ctx.append(cleanup_context)

    app.router.add_view('/connect', MessangerView)

    client = await aiohttp_client(app, cookies={'_uuid': 'none'})

    ws = await client.ws_connect('/connect')

    msg = await ws.receive()

    assert msg == ''

    await ws.close()
