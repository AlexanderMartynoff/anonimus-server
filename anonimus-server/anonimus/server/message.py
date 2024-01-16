from __future__ import annotations
import enum
from dataclasses import field
from time import time
from uuid import uuid4, UUID
from pydantic.dataclasses import dataclass
from pydantic import BaseModel


class Media(BaseModel):
    value: bytes
    name: str


@dataclass(kw_only=True)
class Element:
    id: UUID = field(default_factory=uuid4)
    time: float = field(default_factory=time)
    sender: str | None = None
    receiver: str | None = None


@dataclass(kw_only=True)
class Message:
    text: str
    media: Media | None = None


@dataclass(kw_only=True)
class Greeting:
    sender: str

