import argparse
from aiohttp import web
from anonimus.server.route import routes
from anonimus.server import service


parser = argparse.ArgumentParser()

parser.add_argument('--port', default=9090, type=int)
parser.add_argument('--ssl', default=False, type=bool)

arguments = parser.parse_args()


def run() -> None:
    app = web.Application()

    app.on_startup.append(service.on_startup)
    app.on_shutdown.append(service.on_shutdown)

    app.add_routes(routes)

    web.run_app(app, port=arguments.port)
