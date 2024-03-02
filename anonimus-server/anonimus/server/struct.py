import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field


class Media(Struct, kw_only=True):
    value: bytes


class Record(Struct, kw_only=True):
    uuid: UUID = field(default_factory=uuid4)
    time: float = field(default_factory=time)


class Message(Record, kw_only=True, tag=True):
    text: str
    chat: str


class Identify(Record, kw_only=True, tag=True):
    name: str


class On(Record, kw_only=True, tag=True):
    name: str


class Off(Record, kw_only=True, tag=True):
    name: str


class Status(Record, kw_only=True, tag=True):
    class Value(enum.Enum):
        ACCEPTED = enum.auto()
        READED = enum.auto()

    value: Value
    message_id: UUID


class Connection[T]:
    def __init__(self, uuid: str, socket: T, context: dict[str, str | None]) -> None:
        self.uuid = uuid
        self.socket = socket
        self.context = context
        self.streams: set[str] = set()
