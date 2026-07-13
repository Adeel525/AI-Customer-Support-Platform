"""
Chatbot CRUD API views.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import Chatbot, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from api.serializers import ChatbotCreateSerializer, ChatbotUpdateSerializer
from core.enums import Permission


class ChatbotListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_CHATBOTS.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        try:
            skip = int(request.query_params.get("skip", 0))
            limit = int(request.query_params.get("limit", 50))
        except (TypeError, ValueError):
            skip, limit = 0, 50
        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        qs = Chatbot.objects(workspace_id=ws_id).order_by("-created_at")
        total = qs.count()
        items = [serialize_doc(b) for b in qs.skip(skip).limit(limit)]
        return Response({"items": items, "total": total})

    def post(self, request):
        ws_id = get_workspace_id(request)
        ser = ChatbotCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        bot = Chatbot(
            workspace_id=ws_id,
            name=data["name"],
            welcome_message=data.get("welcome_message", "Hi! How can I help you today?"),
            primary_color=data.get("primary_color", "#10b981"),
            theme=data.get("theme", "light"),
            language=data.get("language", "en"),
            tone=data.get("tone", "professional"),
            personality=data.get("personality", "support"),
            avatar_url=data.get("avatar_url"),
            document_ids=data.get("document_ids") or [],
            is_active=True,
        )
        bot.save()
        return Response(serialize_doc(bot), status=status.HTTP_201_CREATED)


class ChatbotDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_CHATBOTS.value)]

    def get(self, request, chatbot_id):
        ws_id = get_workspace_id(request)
        bot = Chatbot.objects(id=chatbot_id, workspace_id=ws_id).first()
        if not bot:
            return Response({"detail": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_doc(bot))

    def patch(self, request, chatbot_id):
        ws_id = get_workspace_id(request)
        bot = Chatbot.objects(id=chatbot_id, workspace_id=ws_id).first()
        if not bot:
            return Response({"detail": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = ChatbotUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for key, value in ser.validated_data.items():
            if value is not None:
                setattr(bot, key, value)
        bot.save()
        return Response(serialize_doc(bot))

    def delete(self, request, chatbot_id):
        ws_id = get_workspace_id(request)
        bot = Chatbot.objects(id=chatbot_id, workspace_id=ws_id).first()
        if not bot:
            return Response({"detail": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND)
        bot.delete()
        return Response({"message": "Chatbot deleted"})
