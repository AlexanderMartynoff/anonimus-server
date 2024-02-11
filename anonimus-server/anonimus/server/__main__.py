from typing import AsyncIterator, TypedDict, Any
from contextlib import asynccontextmanager, suppress
from falcon.asgi import App, WebSocket
from starlette.applications import Starlette
from redis.asyncio import Redis, RedisError
from anyio import create_task_group
from asyncio import TaskGroup
from loguru import logger
from anonimus.server import action, service
from anonimus.server.web.routing import Route, WebSocketRoute


def create(): 
    return Starlette(
        lifespan=lifespan,
        exception_handlers={
            Exception: on_exception,
        },
        routes=[
            WebSocketRoute('/api/messanger/connect', action.Messanger)
        ],
    )


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    ''' Setup/Teardown services
    '''

    users = {}
    redis = Redis(
        host='localhost',
        port=6379,
        max_connections=10,
    )

    app.state.redis = redis
    app.state.users = users

    async with create_task_group() as group:
        group.start_soon(service.read_redis, redis, users)
        group.start_soon(service.clear_redis, redis)

        yield

        group.cancel_scope.cancel()

    with suppress(RedisError):
        await redis.aclose()


async def on_exception(requst: Any, exception: Any) -> None:
    logger.exception(exception)