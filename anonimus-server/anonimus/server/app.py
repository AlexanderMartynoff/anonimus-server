from typing import Any
from aiohttp import web
from anonimus.server.setup import setup_connections, setup_redis, setup_aiojobs_scheduler, setup_routes


def create_app(config: dict[str, Any] | None = None):
    app = web.Application()

    setup_routes(app)
    setup_redis(app)
    setup_connections(app)
    setup_aiojobs_scheduler(app)

    return app


def run():
    web.run_app(create_app({}), port=9000)
