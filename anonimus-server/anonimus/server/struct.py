import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field, UNSET, UnsetType as Unset


class Media(Struct, kw_only=True):
    value: bytes


class Element(Struct, kw_only=True):
    id: UUID = field(default_factory=uuid4)
    time: float = field(default_factory=time)
    receiver: str | Unset = UNSET


class Message(Element, kw_only=True, tag=True):
    text: str
    media: Media | Unset = UNSET


class Identify(Element, kw_only=True, tag=True):
    name: str


class On(Element, kw_only=True, tag=True):
    name: str


class Status(Element, kw_only=True, tag=True):
    class Value(enum.Enum):
        ACCEPTED = enum.auto()
        READED = enum.auto()

    value: Value
    message_id: UUID


class Connection(Struct):
    name: str | None = None
