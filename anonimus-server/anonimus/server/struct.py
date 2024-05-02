from uuid import UUID
from time import time
from msgspec import Struct, field


BROADCAST_RECEIVER = '*'


class Record(Struct, kw_only=True):
    pass


class Event(Record, tag='event'):
    name: str


class Message(Record, tag='message'):
    id: str
    text: str
    sequence: int
    chat: str
    sender: str
    receiver: str
    time: float = field(default_factory=time)


class Subscription(Record, tag='subscription'):
    name: str


class WebSocketMessage(Record):
    pass


class MessageRequest(WebSocketMessage, tag='message:request'):
    message: Message


class MessageResponse(WebSocketMessage, tag='message:response'):
    message: Message
    reference: str


class EventReponse(WebSocketMessage, tag='event:response'):
    event: Event
    reference: str


class SubsribeRequest(WebSocketMessage, tag='on:request'):
    subscription: Subscription


class UnsubscribeRequest(WebSocketMessage, tag='off:request'):
    subscription: Subscription


class User(Struct):
    id: str
    name: str
    anonimus: bool = False


class Connection[T]:
    def __init__(self, id: UUID, socket: T, user: User, context: dict[str, str | None]) -> None:
        self.id = id
        self.socket = socket
        self.user = user
        self.context = context
        self.streams: set[str] = set()
