from typing import Protocol
import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field, UNSET, UnsetType as Unset
from falcon.asgi import WebSocket


class Closable(Protocol):
    async def close(self):
        pass


class Media(Struct, kw_only=True):
    value: bytes


class Element(Struct, kw_only=True):
    uuid: UUID = field(default_factory=uuid4)
    time: float = field(default_factory=time)


class Message(Element, kw_only=True, tag=True):
    text: str
    chat: str
    media: Media | Unset = UNSET


class Identify(Element, kw_only=True, tag=True):
    name: str


class On(Element, kw_only=True, tag=True):
    name: str

class Off(Element, kw_only=True, tag=True):
    name: str


class Status(Element, kw_only=True, tag=True):
    class Value(enum.Enum):
        ACCEPTED = enum.auto()
        READED = enum.auto()

    value: Value
    message_id: UUID


class Connection[T: Closable](Struct):
    uuid: str
    socket: T
    events: set[str]

    async def close(self):
        await self.socket.close()
