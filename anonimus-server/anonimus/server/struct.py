import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field



class Record(Struct, kw_only=True, tag=str.lower):
    time: float = field(default_factory=time)


class Message(Record):
    id: str
    text: str
    chat: str
    sequence: int


class Identify(Record):
    name: str


class On(Record):
    name: str


class Off(Record):
    name: str


class Status(Record):
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
