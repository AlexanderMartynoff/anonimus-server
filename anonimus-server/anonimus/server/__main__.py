from aiohttp import web
from aiojobs.aiohttp import setup as aiojobs_setup
from anonimus.server import view
from anonimus.server.setup import cleanup_context


if __name__ == '__main__':
    app = web.Application()

    aiojobs_setup(app)

    app.cleanup_ctx.append(cleanup_context)

    app.router.add_view('/api/messanger/connect', view.MessangerView)
    app.router.add_view('/api/connection', view.ConnectionView)

    web.run_app(app, host='0.0.0.0', port=9000)
