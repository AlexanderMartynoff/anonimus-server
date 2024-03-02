from redis.exceptions import RedisError
from msgspec.json import decode
from loguru import logger
from contextlib import suppress
from aiohttp.web import json_response, Response, View
from anonimus.server.struct import Message, On, Off, Connection
from anonimus.server.api import find_chat_members, put_message
from anonimus.server.toolling.web import WebsocketView, WSMessage, AiohttpRequestMixin
from anonimus.server.service import CONNECTIONS, REDIS


class MessangerView(WebsocketView, AiohttpRequestMixin):
    async def open(self) -> None:
        connections = self.request.app[CONNECTIONS]

        if self.user in connections:
            raise KeyError(f'UUID "{self.user}" already connected')

        connections[self.user] = Connection(self.user, self.websocket, {
            'ref': self.request.query.get('ref'),
        })

        await self._broadcast_send('Open')

    async def close(self, exception: Exception | None = None) -> None:
        connections = self.request.app[CONNECTIONS]

        if self.user in connections:
            del connections[self.user]

        await self._broadcast_send('Close')

        if exception:
            raise exception

    @logger.catch(message='Websocket message processing')
    async def message(self, message: WSMessage) -> None:
        redis = self.request.app[REDIS]
        connection = self.request.app[CONNECTIONS][self.user]

        match decode(message.data, type=On | Off | Message):
            case On(name=name):
                connection.streams.add(name)

            case Off(name=name):
                with suppress(KeyError):
                    connection.streams.remove(name)

            case Message(text=text, chat=chat, uuid=uuid):
                for member in await find_chat_members(redis, chat):
                    await put_message(redis, member, {'type': 'Message', 'uuid': str(uuid), 'text': text, 'sender': self.user, 'chat': chat})

    @logger.catch(message='Onchange webscoket connections')
    async def _broadcast_send(self, event: str | None = None) -> None:
        redis = self.request.app[REDIS]
        connections = self.request.app[CONNECTIONS]

        for uuid in connections.copy():
            with suppress(RedisError):
                await put_message(redis, uuid, {'type': 'Online', 'event': event})


class ConnectionView(View, AiohttpRequestMixin):
    async def get(self) -> Response:
        return json_response([
            {'name': uuid} for uuid in self.request.app[CONNECTIONS]
        ])
