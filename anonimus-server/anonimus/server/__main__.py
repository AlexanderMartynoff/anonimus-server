from falcon.asgi import App, WebSocket
from redis.asyncio import Redis
from loguru import logger
from anonimus.server import route, struct


def create():
    app = App()

    redis = Redis(host='localhost', port=6379)
    connections: dict[WebSocket, struct.Connection] = {}

    app.add_route('/api/messanger/connect', route.Messanger(redis, connections))
    app.add_route('/api/status', route.Status())
    app.add_route('/api/contact', route.Contact(connections))

    return app
