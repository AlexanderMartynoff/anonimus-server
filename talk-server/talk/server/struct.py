import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field, json, UNSET, UnsetType as Unset


EOM = b'\0'


class Media(Struct, kw_only=True):
    value: bytes
    name: str


class Element(Struct, kw_only=True):
    id: UUID = field(default_factory=uuid4)
    time: float = field(default_factory=time)
    sender: str
    receiver: str


class Message(Element, kw_only=True, tag=True):
    value: str | Unset = UNSET
    media: Media | Unset = UNSET


class Identity(Element, kw_only=True, tag=True):
    password: str


class Heartbeat(Element, kw_only=True, tag=True):
    pass


class Status(Element, kw_only=True, tag=True):
    class Value(enum.Enum):
        ACCEPTED = enum.auto()
        READED = enum.auto()

    value: Value
    message_id: UUID


def status(message: Message, value: Status.Value) -> Status:
    return Status(
        sender=message.receiver,
        receiver=message.sender,
        message_id=message.id,
        value=value)


def decode(data: bytes) -> Element:
    if data[-1:] == EOM:
        data = data[:-1]

    return json.decode(data, type=Message | Identity | Heartbeat | Status)


def encode(message: Element, terminate: bool = True) -> bytes:
    data = json.encode(message)

    if terminate:
        data += EOM

    return data
