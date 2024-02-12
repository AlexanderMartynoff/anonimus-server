from redis.asyncio import Redis
from redis.exceptions import RedisError
from msgspec.json import decode
from functools import cached_property
from loguru import logger
from contextlib import suppress
from aiohttp.web import json_response, Response, HTTPBadRequest
from anonimus.server.struct import Message, On, Off, Connection
from anonimus.server.api import find_chat_members, put_message
from anonimus.server.toolling.aiohttp import WebsocketView, WSMessage, View
from anonimus.server.service import CONNECTIONS, REDIS


class MessangerView(WebsocketView):
    async def open(self) -> None:
        try:
            self.uuid
        except KeyError:
            raise HTTPBadRequest(text='Cookie "uuid" is required')

        connections = self.request.app[CONNECTIONS]

        if self.uuid in connections:
            raise ValueError()

        connections[self.uuid] = Connection(self.uuid, self.websocket, {
            'ref': self.request.query.get('ref'),
        })

        await self._on_change()

    async def close(self, exception: Exception | None = None) -> None:
        connections = self.request.app[CONNECTIONS]

        if self.uuid in connections:
            del connections[self.uuid]

        await self._on_change()

    @logger.catch(Exception, reraise=False, message='Websocket message processing')
    async def message(self, message: WSMessage) -> None:
        redis = self.request.app[REDIS]
        connection = self.request.app[CONNECTIONS][self.uuid]

        record = decode(message.data, type=On | Off | Message)

        match record:
            case On(name=name):
                connection.streams.add(name)

            case Off(name=name):
                with suppress(KeyError):
                    connection.streams.remove(name)

            case Message(text=text, chat=chat, uuid=uuid, sender=sender):
                for member in await find_chat_members(redis, chat):
                    await put_message(redis, member, {'type': 'Message', 'uuid': str(uuid), 'text': text, 'sender': sender})

    async def _on_change(self, event: str | None = None) -> None:
        redis = self.request.app[REDIS]
        connections = self.request.app[CONNECTIONS]

        for uuid in connections:
            with suppress(RedisError):
                await put_message(redis, uuid, {'type': 'Online'})

    @cached_property
    def uuid(self):
        return self.request.cookies['uuid']


class ConnectionView(View):
    async def get(self) -> Response:
        return json_response([uuid for uuid in self.request.app[CONNECTIONS]])

