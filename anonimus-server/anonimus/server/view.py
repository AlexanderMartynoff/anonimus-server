from asyncio import ensure_future
from redis.exceptions import RedisError
from msgspec.json import decode
from msgspec import to_builtins
from msgspec.structs import replace
from loguru import logger
from contextlib import suppress
from aiohttp.web import json_response, Response, View
from anonimus.server.struct import MessageRequest, SubsribeRequest, UnsubscribeRequest, Connection, BROADCAST_RECEIVER
from anonimus.server.api import fetch_chat_members, add_message
from anonimus.server.toolling.web import WebsocketView, WSMessage, AiohttpRequestMixin
from anonimus.server.worker import CONNECTIONS, REDIS


class MessangerView(WebsocketView, AiohttpRequestMixin):
    async def open(self) -> None:
        connections = self.request.app[CONNECTIONS]

        if self.id in connections:
            raise KeyError(f'UUID "{self.id}" already connected')

        connections[self.id] = Connection(self.id, self.websocket, None, {
            'ref': self.request.query.get('ref'),
        })

        self._emit('open')

    async def close(self, exception: Exception | None = None) -> None:
        connections = self.request.app[CONNECTIONS]

        if self.id in connections:
            del connections[self.id]

        self._emit('close')

        if exception:
            raise exception

    @logger.catch(message='Websocket message processing')
    async def message(self, ws_message: WSMessage) -> None:
        redis = self.request.app[REDIS]
        connection = self.request.app[CONNECTIONS][self.id]

        match decode(ws_message.data, type=MessageRequest | SubsribeRequest | UnsubscribeRequest, strict=False):
            case SubsribeRequest(subscription=subscription):
                connection.streams.add(subscription.name)

            case UnsubscribeRequest(subscription=subscription):
                with suppress(KeyError):
                    connection.streams.remove(subscription.name)

            case MessageRequest(message=message):
                if message.receiver == BROADCAST_RECEIVER:
                    for member in await fetch_chat_members(redis, message.chat):
                        await add_message(redis, member, to_builtins(replace(message, receiver=member)))

                    return

                await add_message(redis, message.receiver, to_builtins(message))

    @logger.catch(message='Onchange webscoket connections')
    def _emit(self, event: str | None = None) -> None:
        redis = self.request.app[REDIS]
        connections = self.request.app[CONNECTIONS]

        for id in connections:
            with suppress(RedisError):
                ensure_future(add_message(redis, id, {'type': 'event', 'name': event}))


class OnlineUserView(View, AiohttpRequestMixin):
    async def get(self) -> Response:
        return json_response([
            {'name': id} for id in self.request.app[CONNECTIONS]
        ])
