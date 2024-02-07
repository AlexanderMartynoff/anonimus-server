from falcon.asgi import App, WebSocket
from redis.asyncio import Redis
from loguru import logger
from anonimus.server import action, struct, middleware


def create():
    redis = Redis(
        host='localhost',
        port=6379,
        max_connections=10,
    )

    connections: dict[bytes, struct.Connection] = {}

    app = App(
        middleware=[middleware.BackgroundWorker(redis, connections)],
    )

    app.add_route('/api/messanger/connect', action.Messanger(redis, connections))
    app.add_route('/api/status', action.Status())
    app.add_route('/api/contact', action.People(connections))

    return app
