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

    connections: dict[str, struct.Connection[WebSocket]] = {}

    app = App(
        middleware=[middleware.BackgroundWorker(redis, connections)],
    )

    app.add_route('/api/messanger/connect', action.Messanger(redis, connections))
    app.add_route('/api/status', action.Status())
    app.add_route('/api/who-online', action.WhoOnline(connections))

    app.add_error_handler(Exception, _on_error)

    return app


async def _on_error(requst, response, error, params, ws=None):
    logger.exception(error)
