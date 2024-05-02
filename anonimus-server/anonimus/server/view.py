from asyncio import ensure_future
from msgspec.json import decode
from msgspec import to_builtins
from msgspec.structs import replace
from loguru import logger
from contextlib import suppress
from aiohttp.web import json_response, Response, View
from anonimus.server.struct import MessageRequest, SubsribeRequest, UnsubscribeRequest, Connection, BROADCAST_RECEIVER
from anonimus.server.api import fetch_chat_members, send_message
from anonimus.server.addon.aiohttp import WebsocketView, WSMessage
from anonimus.server.worker import CONNECTIONS, KAFKA_CONSUMER
from anonimus.server.web import AiohttpViewUserMixin, AiohttpViewIdMixin


class MessangerView(WebsocketView, AiohttpViewUserMixin, AiohttpViewIdMixin):
    async def open(self) -> None:
        connections = self.request.app[CONNECTIONS]

        connections[self.id] = Connection(self.id, self.websocket, self.user, {
            'ref': self.request.query.get('ref'),
        })

        self._emit('open')

    async def close(self, exception: Exception | None = None) -> None:
        connections = self.request.app[CONNECTIONS]

        try:
            del connections[self.id]
        except KeyError:
            pass

        self._emit('close')

        if exception:
            raise exception

    @logger.catch(message='Websocket message processing')
    async def message(self, ws_message: WSMessage) -> None:
        kafka = self.request.app[KAFKA_CONSUMER]
        connection = self.request.app[CONNECTIONS][self.id]

        match decode(ws_message.data, type=MessageRequest | SubsribeRequest | UnsubscribeRequest, strict=False):
            case SubsribeRequest(subscription=subscription):
                connection.streams.add(subscription.name)

            case UnsubscribeRequest(subscription=subscription):
                with suppress(KeyError):
                    connection.streams.remove(subscription.name)

            case MessageRequest(message=message):
                if message.receiver == BROADCAST_RECEIVER:
                    for member in await fetch_chat_members(kafka, message.chat):
                        await send_message(kafka, member, to_builtins(replace(message, receiver=member)))

                    return

                await send_message(kafka, message.receiver, to_builtins(message))

    @logger.catch(message='Onchange webscoket connections')
    def _emit(self, event: str) -> None:
        redis = self.request.app[KAFKA_CONSUMER]
        connections = self.request.app[CONNECTIONS]

        for connection in connections.values():
            with suppress(RedisError):
                ensure_future(send_message(redis, connection.user.id, {'type': 'event', 'name': event}))


class OnlineUserView(View, AiohttpViewUserMixin):
    async def get(self) -> Response:
        return json_response([
            {'name': id} for id in self.request.app[CONNECTIONS]
        ])


class AuthenticationView(View, AiohttpViewUserMixin):
    async def get(self) -> Response:
        return json_response({'id': None, 'name': None})
