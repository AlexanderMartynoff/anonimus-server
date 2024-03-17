from typing import Iterable
from aiohttp.web import View, Request, WebSocketResponse
from aiohttp.http_websocket import WSMessage


class WebsocketView(View):
    timeout: float = 10.0
    receive_timeout: float | None = None
    autoclose: bool = True
    autoping: bool = True
    heartbeat: float  | None = None
    protocols: Iterable[str] = ()
    compress: bool = True
    max_msg_size: int = 4 * 1024 * 1024

    async def get(self):
        self._websocket = WebSocketResponse(
            timeout=self.timeout,
            receive_timeout=self.receive_timeout,
            autoclose=self.autoclose,
            heartbeat=self.heartbeat,
            protocols=self.protocols,
            compress=self.compress,
            max_msg_size=self.max_msg_size,
        )

        await self._websocket.prepare(self.request)

        try:
            await self.open()
            async for ws_message in self._websocket:
                await self.message(ws_message)
        except Exception as exception:
            await self.close(exception)
        else:
            await self.close()

        return self._websocket

    async def open(self):
        raise NotImplementedError()

    async def close(self, exception: Exception | None = None):
        raise NotImplementedError()

    async def message(self, ws_message: WSMessage):
        raise NotImplementedError()

    @property
    def websocket(self) -> WebSocketResponse:
        return self._websocket


class AiohttpRequestMixin:
    request: Request

    @property
    def id(self) -> str:
        return self.request.cookies['id']
