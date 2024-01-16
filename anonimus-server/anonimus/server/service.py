from typing import Any
from collections import defaultdict
from dataclasses import dataclass, field
from weakref import WeakSet, WeakValueDictionary
from redis.asyncio import Redis, BlockingConnectionPool


@dataclass
class Connection:
    PHANTOM = 0
    USER = 1

    socket: None
    sender: str | None = None
    events: set[str] = field(default_factory=set)
    state: int = PHANTOM
    user: Any = None


async def redis():
    # Redis.from_pool()

    redis = Redis(host='localhost', port=6379)

    try:
        yield redis
    except Exception:
        pass

    await redis.aclose()

