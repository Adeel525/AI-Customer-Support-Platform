"""
Admin analytics assistant view.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.permissions import IsAuthenticatedJWT, IsOwnerOrAdmin
from api.views.analytics import _overview
from core.ai.llm_client import LLMClient


class AdminAssistantQueryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, IsOwnerOrAdmin]

    def post(self, request):
        question = request.data.get("question") or request.query_params.get("question")
        if not question:
            return Response({"detail": "question is required"}, status=status.HTTP_400_BAD_REQUEST)

        ws_id = get_workspace_id(request)
        overview = _overview(ws_id)
        context = f"Analytics data: {overview}"
        answer = LLMClient().generate([
            {
                "role": "system",
                "content": "You are an admin analytics assistant. Answer based on the provided data.",
            },
            {"role": "user", "content": f"Data:\n{context}\n\nQuestion: {question}"},
        ])
        return Response({"answer": answer, "data": overview})
