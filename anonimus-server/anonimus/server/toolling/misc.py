from typing import Callable, Coroutine
from asyncio import sleep


type CoroutineFunction[Y, S, T] = Callable[..., Coroutine[Y, S, T]]


def repeat[Y, S, T](exception_cls, timeout, exception_timeout) -> Callable[[CoroutineFunction[Y, S, T]], CoroutineFunction[Y, S, T]]:
    def decorator(function: CoroutineFunction[Y, S, T]) -> CoroutineFunction[Y, S, T]:
        async def repeater[**P](*args: P.args, **kwargs: P.kwargs) -> T:
            while True:
                try:
                    await function(*args, **kwargs)
                except exception_cls:
                    await sleep(exception_timeout)
                else:
                    await sleep(timeout)

        return repeater

    return decorator
