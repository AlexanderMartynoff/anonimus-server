from typing import Awaitable, Callable, Coroutine, Any
import asyncio


def repeat[Y, S, T](function: Callable[..., Coroutine[Y, S, T]]) -> Callable[..., Coroutine[Y, S, T]]:
    async def repeater[**P](*args: P.args, **kwargs: P.kwargs) -> T:
        while True:
            await asyncio.gather(function(*args, **kwargs), asyncio.sleep(0))

    return repeater
