import json
from redis.exceptions import RedisError
from msgspec.json import decode
from loguru import logger
from contextlib import suppress
from aiohttp.web import json_response, Response, View
from anonimus.server.struct import Message, On, Off, Connection
from anonimus.server.api import find_chat_members, add_message
from anonimus.server.toolling.web import WebsocketView, WSMessage, AiohttpRequestMixin
from anonimus.server.service import CONNECTIONS, REDIS


class MessangerView(WebsocketView, AiohttpRequestMixin):
    async def open(self) -> None:
        connections = self.request.app[CONNECTIONS]

        if self.id in connections:
            raise KeyError(f'UUID "{self.id}" already connected')

        connections[self.id] = Connection(self.id, self.websocket, {
            'ref': self.request.query.get('ref'),
        })

        await self._emit('open')

    async def close(self, exception: Exception | None = None) -> None:
        connections = self.request.app[CONNECTIONS]

        if self.id in connections:
            del connections[self.id]

        await self._emit('close')

        if exception:
            raise exception

    @logger.catch(message='Websocket message processing')
    async def message(self, message: WSMessage) -> None:
        redis = self.request.app[REDIS]
        connection = self.request.app[CONNECTIONS][self.id]

        match decode(message.data, type=On | Off | Message, strict=False):
            case On(name=name):
                connection.streams.add(name)

            case Off(name=name):
                with suppress(KeyError):
                    connection.streams.remove(name)

            case Message(text=text, chat=chat, id=id):
                for member in await find_chat_members(redis, chat):
                    await add_message(redis, member, {'type': 'message', 'id': id, 'text': text, 'sender': self.id, 'chat': chat})

    @logger.catch(message='Onchange webscoket connections')
    async def _emit(self, event: str | None = None) -> None:
        redis = self.request.app[REDIS]
        connections = self.request.app[CONNECTIONS]

        for id in connections:
            with suppress(RedisError):
                await add_message(redis, id, {'type': 'online', 'event': event})


class OnlineUserView(View, AiohttpRequestMixin):
    async def get(self) -> Response:
        return json_response([
            {'name': id} for id in self.request.app[CONNECTIONS]
        ])
