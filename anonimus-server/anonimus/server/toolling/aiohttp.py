from typing import Iterable
from inspect import signature
from aiohttp.web import View as AiohttpView, Request, WebSocketResponse
from aiohttp.http_websocket import WSMessage


class View(AiohttpView):
    pass


class WebsocketView(View):
    timeout: float = 10.0
    receive_timeout: float | None = None
    autoclose: bool = True
    autoping: bool = True
    heartbeat: float  | None = None
    protocols: Iterable[str] = ()
    compress: bool = True
    max_msg_size: int = 4 * 1024 * 1024

    def __init__(self, request: Request) -> None:
        super().__init__(request)

        self._websocket = WebSocketResponse(
            timeout=self.timeout,
            receive_timeout=self.receive_timeout,
            autoclose=self.autoclose,
            heartbeat=self.heartbeat,
            protocols=self.protocols,
            compress=self.compress,
            max_msg_size=self.max_msg_size,
        )

    async def get(self):
        await self.websocket.prepare(self.request)

        try:
            await self.open()
            async for message in self.websocket:
                await self.message(message)
        except Exception as exception:
            await self.close(exception)
        finally:
            await self.close()

        return self.websocket

    async def open(self):
        raise NotImplementedError()

    async def close(self, exception: Exception | None = None):
        raise NotImplementedError()

    async def message(self, message: WSMessage):
        raise NotImplementedError()

    @property
    def websocket(self) -> WebSocketResponse:
        return self._websocket
