from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin_assistant,
    analytics,
    api_keys,
    auth,
    billing,
    chat,
    chatbots,
    crawler,
    integrations,
    knowledge,
    search,
    tickets,
    voice,
    websocket,
    workspaces,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(knowledge.router)
api_router.include_router(crawler.router)
api_router.include_router(chatbots.router)
api_router.include_router(chat.router, prefix="/chat")
api_router.include_router(chat.public_router)
api_router.include_router(tickets.router)
api_router.include_router(analytics.router)
api_router.include_router(search.router)
api_router.include_router(integrations.router)
api_router.include_router(billing.router)
api_router.include_router(api_keys.router)
api_router.include_router(admin_assistant.router)
api_router.include_router(voice.router)
api_router.include_router(websocket.router)
