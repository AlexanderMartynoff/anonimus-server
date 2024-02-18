from typing import Any
from pytest_aiohttp.plugin import AiohttpClient
from anonimus.server.setup import CONNECTIONS
from anonimus.server.testing import create_app


UUID = 'anonimus-test'

HTTP_CLIENT_OPTIONS: dict[str, Any] = {
    'cookies': {'uuid': UUID},
}


async def test_connection_view(aiohttp_client: AiohttpClient):
    app = create_app()
    client = await aiohttp_client(app, **HTTP_CLIENT_OPTIONS)

    async with client.ws_connect('/api/messanger/connect'):
        response = await client.get('/api/connection')
        connections = await response.json()

        assert connections == [UUID]


async def test_messanger_view(aiohttp_client: AiohttpClient):
    app = create_app()
    client = await aiohttp_client(app, **HTTP_CLIENT_OPTIONS)

    async with client.ws_connect('/api/messanger/connect'):
        assert UUID in app[CONNECTIONS]

    assert len(app[CONNECTIONS]) == 0


async def test_messanger_view_connect(aiohttp_client: AiohttpClient):
    app = create_app()
    client = await aiohttp_client(app, **HTTP_CLIENT_OPTIONS)

    async with client.ws_connect('/api/messanger/connect') as websocket:
        # receive and skip 'Online' message
        await websocket.receive_json(timeout=3)

        text = 'Helo, World!'

        await websocket.send_json({
            'type': 'Message',
            'text': text,
            'chat': UUID,
            'sender': 'sender',
        })

        message = await websocket.receive_json(timeout=3)

        assert message['text'] == text
