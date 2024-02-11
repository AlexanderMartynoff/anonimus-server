from typing import Any, Callable
from inspect import signature
from starlette.requests import HTTPConnection, Request
from starlette.websockets import WebSocket
from starlette.types import Scope, Send, Receive
from starlette.routing import WebSocketRoute as StarletteWebSocketRoute, Route as StarletteRoute


class WebSocketRoute(StarletteWebSocketRoute):
    pass


class Route(StarletteRoute):
    pass
