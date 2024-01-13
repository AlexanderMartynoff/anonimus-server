from weakref import WeakSet
from aiohttp.web import Application, AppKey, WebSocketResponse
from redis.asyncio import Redis, client


class Key:
    redis = AppKey('redis', Redis)
    broker = AppKey('broker', client.PubSub)
    socket = AppKey('websocket', WeakSet[WebSocketResponse])


async def on_startup(app: Application):
    app[Key.socket] = WeakSet()
    app[Key.redis] = Redis(host='localhost', port=6379)


async def on_shutdown(app: Application):
    app[Key.socket].clear()
    await app[Key.redis].aclose()
