import argparse
from aiohttp import web
from anonimus.server.route import routes


parser = argparse.ArgumentParser()

parser.add_argument('--port', default=9090, type=int)
parser.add_argument('--ssl', default=False, type=bool)

arguments = parser.parse_args()


def run() -> None:
    appplication = web.Application()
    appplication.add_routes(routes)

    web.run_app(appplication, port=arguments.port)
