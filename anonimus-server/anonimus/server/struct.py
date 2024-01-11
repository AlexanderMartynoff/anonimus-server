from __future__ import annotations
import enum
from time import time
from uuid import uuid4, UUID
from msgspec import Struct, field, UNSET, UnsetType as Unset


class Media(Struct, kw_only=True):
    value: bytes
    name: str


class Element(Struct, kw_only=True):
    id: UUID = field(default_factory=uuid4)
    time: float = field(default_factory=time)
    sender: str | Unset = UNSET
    receiver: str | Unset = UNSET


class Message(Element, kw_only=True, tag=True):
    text: str
    media: Media | Unset = UNSET


class Registration(Element, kw_only=True, tag=True):
    pass


class Subscription(Element, kw_only=True, tag=True):
    pass


class Ping(Element, kw_only=True, tag=True):
    def reverse(self) -> Pong:
        return Pong(sender=self.receiver, receiver=self.sender)


class Pong(Element, kw_only=True, tag=True):
    def reverse(self) -> Ping:
        return Ping(sender=self.receiver, receiver=self.sender)


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
