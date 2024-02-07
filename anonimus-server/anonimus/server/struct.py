from typing import Protocol
import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field, UNSET, UnsetType as Unset
from falcon.asgi import WebSocket
from contextlib import contextmanager, asynccontextmanager, suppress

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


class Connection[T: Closable]:
    def __init__(self, uuid: str, socket: T, context: dict[str, str]) -> None:
        self.uuid = uuid
        self.socket = socket
        self.context = context
        self.streams: set[str] = set()

    async def close(self):
        await self.socket.close()


class ConnectionManager[T: Closable]:
    def __init__(self) -> None:
        self._connections: dict[str, Connection[T]] = {}

    @asynccontextmanager
    async def open(self, uuid: str):
        self._connections[uuid] = Connection(uuid)  # type: ignore

        try:
            yield self._connections[uuid]
        finally:
            try:
                await self._connections[uuid].close()
            finally:
                if uuid in self._connections:
                    del self._connections[uuid]
