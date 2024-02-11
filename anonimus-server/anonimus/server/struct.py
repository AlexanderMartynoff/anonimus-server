from typing import Protocol, AsyncGenerator, AsyncIterable
import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field, UNSET, UnsetType as Unset
from falcon.asgi import WebSocket
from contextlib import asynccontextmanager, suppress


class Socket(Protocol):
    async def close(self): ...
    async def accept(self): ...


class Media(Struct, kw_only=True):
    value: bytes


class Element(Struct, kw_only=True):
    uuid: UUID = field(default_factory=uuid4)
    time: float = field(default_factory=time)


class Message(Element, kw_only=True, tag=True):
    text: str
    chat: str
    sender: str


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


class Connection[T: Socket]:
    def __init__(self, uuid: str, socket: T, context: dict[str, str | None]) -> None:
        self.uuid = uuid
        self.socket = socket
        self.context = context
        self.streams: set[str] = set()
