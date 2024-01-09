from typing import Any
from collections.abc import MutableMapping
from aiohttp.web import WebSocketResponse, RouteTableDef, Request, AppKey
from .api import Redis


redis = AppKey('redis', Redis)
