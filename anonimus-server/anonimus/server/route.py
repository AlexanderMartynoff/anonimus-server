from __future__ import annotations
from fastapi import APIRouter, WebSocket, Depends
from starlette.websockets import WebSocketDisconnect
from typing import Annotated
from redis.asyncio import Redis
from pydantic import TypeAdapter
from .service import Connection, redis


router = APIRouter()


@router.websocket('/api/messanger/connect')
async def connect(websocket: WebSocket, redis: Annotated[Redis, Depends(redis)]):
    await websocket.accept()

    while websocket:
        try:
            values = await websocket.receive_json()
        except WebSocketDisconnect:
            break

        if not values:
            continue

        match values:
            case {'type': 'On'}:
                pass

            case {'type': 'Off'}:
                pass

        print(values)
