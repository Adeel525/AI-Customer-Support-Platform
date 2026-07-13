"""
Integrations API views — list, connect, disconnect, webhook stubs.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import Integration, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from core.enums import Permission


class IntegrationListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_INTEGRATIONS.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        items = [serialize_doc(i) for i in Integration.objects(workspace_id=ws_id)]
        return Response({"items": items, "total": len(items)})


class IntegrationConnectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_INTEGRATIONS.value)]

    def post(self, request, integration_type):
        ws_id = get_workspace_id(request)
        config = request.data if isinstance(request.data, dict) else {}
        # Allow nested "config" key
        if "config" in config and isinstance(config["config"], dict):
            config = config["config"]

        integration = Integration(
            workspace_id=ws_id,
            type=integration_type,
            config=config,
            is_active=True,
        )
        integration.save()
        return Response(serialize_doc(integration), status=status.HTTP_201_CREATED)


class IntegrationDisconnectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_INTEGRATIONS.value)]

    def delete(self, request, integration_id):
        ws_id = get_workspace_id(request)
        integration = Integration.objects(id=integration_id, workspace_id=ws_id).first()
        if not integration:
            return Response({"detail": "Integration not found"}, status=status.HTTP_404_NOT_FOUND)
        integration.delete()
        return Response({"message": "Integration disconnected"})


class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {"detail": "whatsapp webhook handler not yet implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class SlackWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {"detail": "slack webhook handler not yet implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
