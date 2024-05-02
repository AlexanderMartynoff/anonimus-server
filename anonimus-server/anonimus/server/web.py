from uuid import uuid4, UUID
from urllib.parse import unquote
from msgspec.json import decode
from aiohttp.web import Request
from anonimus.server.struct import User


class AiohttpViewUserMixin:
    request: Request

    @property
    def user(self) -> User:
        if 'user' not in self.request:
            if user := self.request.cookies.get('user'):
                user = decode(unquote(user), type=User, strict=False)
            else:
                user = User('0', '0', True)

            self.request['user'] = user

        return self.request['user']


class AiohttpViewIdMixin:
    request: Request

    @property
    def id(self) -> UUID:
        if 'id' not in self.request:
            self.request['id'] = uuid4()

        return self.request['id']    
