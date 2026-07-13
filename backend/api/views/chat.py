"""
Chat API views — public widget endpoints and authenticated conversation management.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import (
    Chatbot,
    Conversation,
    DocumentChunk,
    Feedback,
    Message,
    Ticket,
    serialize_doc,
)
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from api.serializers import ChatMessageSerializer, FeedbackSerializer
from core.ai.llm_client import LLMClient
from core.ai.prompts.support import TICKET_SUMMARY_PROMPT
from core.ai.rag_engine import RAGEngine
from core.enums import ConversationStatus, MessageRole, Permission, TicketPriority, TicketStatus

logger = logging.getLogger(__name__)


class ChunkRepoAdapter:
    """Adapter so RAGEngine can run keyword search over DocumentChunk."""

    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id

    def keyword_search(self, query: str, limit: int = 10) -> list[dict]:
        if not query:
            return []
        chunks = DocumentChunk.objects(
            workspace_id=self.workspace_id,
            content__icontains=query[:100],
        )[:limit]
        return [serialize_doc(c) for c in chunks]


def _auto_create_ticket(workspace_id: str, conversation_id: str, last_message: str, rag_result: dict) -> dict:
    messages = list(Message.objects(conversation_id=conversation_id).order_by("created_at"))
    conv_text = "\n".join(f"{m.role}: {m.content}" for m in messages)

    ai_data: dict = {
        "title": f"Escalation: {last_message[:80]}",
        "summary": conv_text[:500],
        "detected_intent": "support_request",
        "suggested_resolution": "Review conversation and respond to customer.",
        "priority": TicketPriority.MEDIUM.value,
        "category": "technical",
    }
    try:
        prompt = TICKET_SUMMARY_PROMPT.format(conversation=conv_text[:3000])
        response = LLMClient().generate(
            [{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500,
        )
        parsed = json.loads(response)
        if isinstance(parsed, dict):
            ai_data.update(parsed)
    except Exception:
        logger.debug("Ticket AI summary failed; using defaults", exc_info=True)

    ticket = Ticket(
        workspace_id=workspace_id,
        title=ai_data.get("title", f"Escalation: {last_message[:80]}"),
        description=last_message,
        category=ai_data.get("category", "technical"),
        priority=ai_data.get("priority", TicketPriority.MEDIUM.value),
        status=TicketStatus.OPEN.value,
        conversation_id=conversation_id,
        ai_summary=ai_data.get("summary", conv_text[:500]),
        detected_intent=ai_data.get("detected_intent", "support_request"),
        suggested_resolution=ai_data.get("suggested_resolution", ""),
        confidence_at_escalation=rag_result.get("confidence", 0),
        auto_generated=True,
    )
    ticket.save()
    return serialize_doc(ticket)


class PublicChatbotConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, chatbot_id):
        bot = Chatbot.objects(id=chatbot_id, is_active=True).first()
        if not bot:
            return Response({"detail": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "id": str(bot.id),
            "name": bot.name,
            "welcome_message": bot.welcome_message,
            "primary_color": bot.primary_color,
            "theme": bot.theme,
            "avatar_url": bot.avatar_url,
        })


class PublicChatMessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, chatbot_id):
        bot = Chatbot.objects(id=chatbot_id, is_active=True).first()
        if not bot:
            return Response({"detail": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = ChatMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        workspace_id = bot.workspace_id
        message_text = data["message"]
        conversation_id = data.get("conversation_id") or None
        customer_id = data.get("customer_id") or str(uuid.uuid4())

        if not conversation_id:
            conversation = Conversation(
                workspace_id=workspace_id,
                chatbot_id=chatbot_id,
                customer_id=customer_id,
                status=ConversationStatus.ACTIVE.value,
                message_count=0,
            )
            conversation.save()
            conversation_id = str(conversation.id)
        else:
            conversation = Conversation.objects(
                id=conversation_id,
                workspace_id=workspace_id,
            ).first()
            if not conversation:
                return Response({"detail": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        Message(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            role=MessageRole.USER.value,
            content=message_text,
        ).save()

        history = list(Message.objects(conversation_id=conversation_id).order_by("created_at"))
        history_msgs = [{"role": m.role, "content": m.content} for m in history]

        chatbot_config = serialize_doc(bot) or {}
        rag = RAGEngine(workspace_id, chunk_repo=ChunkRepoAdapter(workspace_id))
        try:
            rag_result = rag.query(
                message_text,
                chatbot_config=chatbot_config,
                conversation_history=history_msgs,
            )
        except Exception:
            logger.exception("RAG query failed")
            rag_result = {
                "content": "I'm having trouble answering right now. Please try again or contact support.",
                "confidence": 0.0,
                "sources": [],
                "should_escalate": True,
            }

        assistant_msg = Message(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            role=MessageRole.ASSISTANT.value,
            content=rag_result["content"],
            confidence=rag_result.get("confidence"),
            sources=rag_result.get("sources") or [],
        )
        assistant_msg.save()

        conversation = Conversation.objects(id=conversation_id).first()
        if conversation:
            conversation.message_count = len(history) + 1
            conversation.last_message_at = datetime.now(timezone.utc)
            conversation.last_confidence = rag_result.get("confidence")
            if rag_result.get("should_escalate"):
                conversation.status = ConversationStatus.ESCALATED.value
            conversation.save()

        if rag_result.get("should_escalate"):
            try:
                _auto_create_ticket(workspace_id, conversation_id, message_text, rag_result)
            except Exception:
                logger.exception("Auto ticket creation failed")

        return Response({
            "conversation_id": conversation_id,
            "message_id": str(assistant_msg.id),
            "content": rag_result["content"],
            "confidence": rag_result.get("confidence"),
            "sources": rag_result.get("sources") or [],
            "should_escalate": bool(rag_result.get("should_escalate")),
        })


class PublicEscalateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, chatbot_id):
        bot = Chatbot.objects(id=chatbot_id, is_active=True).first()
        if not bot:
            return Response({"detail": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND)

        conversation_id = request.data.get("conversation_id") or request.query_params.get("conversation_id")
        if not conversation_id:
            return Response({"detail": "conversation_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects(
            id=conversation_id,
            workspace_id=bot.workspace_id,
        ).first()
        if not conversation:
            return Response({"detail": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        conversation.status = ConversationStatus.ESCALATED.value
        conversation.save()

        messages = list(Message.objects(conversation_id=conversation_id).order_by("created_at"))
        last_user = next(
            (m.content for m in reversed(messages) if m.role == MessageRole.USER.value),
            "Customer requested human support",
        )
        ticket = _auto_create_ticket(
            bot.workspace_id,
            conversation_id,
            last_user,
            {"confidence": 0.0, "content": ""},
        )
        return Response(ticket, status=status.HTTP_201_CREATED)


class PublicFeedbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = FeedbackSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        msg = Message.objects(id=data["message_id"]).first()
        if not msg:
            return Response({"detail": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

        feedback = Feedback(
            workspace_id=msg.workspace_id,
            message_id=data["message_id"],
            rating=data.get("rating"),
            comment=data.get("comment") or None,
            thumbs=data.get("thumbs"),
        )
        feedback.save()
        return Response(serialize_doc(feedback), status=status.HTTP_201_CREATED)


class ConversationListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.LIVE_CHAT.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        status_filter = request.query_params.get("status")
        try:
            skip = int(request.query_params.get("skip", 0))
            limit = int(request.query_params.get("limit", 50))
        except (TypeError, ValueError):
            skip, limit = 0, 50
        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        qs = Conversation.objects(workspace_id=ws_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        qs = qs.order_by("-last_message_at", "-created_at")
        total = qs.count()
        items = [serialize_doc(c) for c in qs.skip(skip).limit(limit)]
        return Response({"items": items, "total": total})


class ConversationDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.LIVE_CHAT.value)]

    def get(self, request, conversation_id):
        ws_id = get_workspace_id(request)
        conv = Conversation.objects(id=conversation_id, workspace_id=ws_id).first()
        if not conv:
            return Response({"detail": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)
        messages = [
            serialize_doc(m)
            for m in Message.objects(conversation_id=conversation_id).order_by("created_at")
        ]
        data = serialize_doc(conv)
        data["messages"] = messages
        return Response(data)


class ConversationAssignView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.LIVE_CHAT.value)]

    def post(self, request, conversation_id):
        ws_id = get_workspace_id(request)
        agent_id = request.data.get("agent_id") or request.query_params.get("agent_id")
        if not agent_id:
            return Response({"detail": "agent_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        conv = Conversation.objects(id=conversation_id, workspace_id=ws_id).first()
        if not conv:
            return Response({"detail": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        conv.assigned_agent_id = agent_id
        conv.save()
        return Response(serialize_doc(conv))
