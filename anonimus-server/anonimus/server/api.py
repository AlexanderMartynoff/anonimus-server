from typing import Any
from redis.asyncio import Redis


async def get_chat_members(redis: Redis, chat: str) -> set[str]:
    return {chat}


async def send_member_message(redis: Redis, member: str, message: dict[Any, Any]):
    await redis.xadd(member, message)
