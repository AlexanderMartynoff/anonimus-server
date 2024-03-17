from typing import Any
from redis.asyncio import Redis


async def fetch_chat_members(redis: Redis, chat: str) -> set[str]:
    return set()


async def add_message(redis: Redis, receiver: str, message: dict[Any, Any]) -> None:
    await redis.xadd(receiver, message)
