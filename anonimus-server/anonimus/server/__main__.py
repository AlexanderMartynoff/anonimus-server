from fastapi import FastAPI
from anonimus.server.route import router
from anonimus.server import service
from anonimus.server import task


api = FastAPI(
    title='Anonimus',
    summary='Anonimus server (WebSocket based chat)',
)

api.include_router(router)
