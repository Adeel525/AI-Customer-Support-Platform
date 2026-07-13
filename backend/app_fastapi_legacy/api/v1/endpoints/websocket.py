import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])

active_connections: dict[str, list[WebSocket]] = {}


@router.websocket("/ws/conversations/{conversation_id}")
async def conversation_ws(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    if conversation_id not in active_connections:
        active_connections[conversation_id] = []
    active_connections[conversation_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type", "message")

            if msg_type == "typing":
                await _broadcast(conversation_id, {"type": "typing", "user_id": message.get("user_id")}, websocket)
            elif msg_type == "message":
                db = get_database()
                from app.repositories.message_repository import MessageRepository
                from app.models.enums import MessageRole
                msg_repo = MessageRepository(db)
                saved = await msg_repo.create({
                    "conversation_id": conversation_id,
                    "workspace_id": message.get("workspace_id", ""),
                    "role": MessageRole.AGENT.value,
                    "content": message.get("content", ""),
                    "author_id": message.get("user_id"),
                })
                await _broadcast(conversation_id, {"type": "message", "data": saved})
            elif msg_type == "seen":
                await _broadcast(conversation_id, {"type": "seen", "user_id": message.get("user_id")}, websocket)
    except WebSocketDisconnect:
        active_connections[conversation_id].remove(websocket)
        if not active_connections[conversation_id]:
            del active_connections[conversation_id]


async def _broadcast(conversation_id: str, data: dict, exclude: WebSocket | None = None):
    connections = active_connections.get(conversation_id, [])
    for ws in connections:
        if ws != exclude:
            try:
                await ws.send_json(data)
            except Exception:
                pass
