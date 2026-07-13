"""
API key management views.
"""
from __future__ import annotations

import hashlib
import secrets

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import ApiKey, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from core.enums import Permission


class ApiKeyListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_WORKSPACE.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        items = []
        for key in ApiKey.objects(workspace_id=ws_id).order_by("-created_at"):
            data = serialize_doc(key) or {}
            data.pop("key_hash", None)
            items.append(data)
        return Response({"items": items, "total": len(items)})

    def post(self, request):
        ws_id = get_workspace_id(request)
        name = request.data.get("name") or request.query_params.get("name")
        if not name:
            return Response({"detail": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

        permissions = request.data.get("permissions") or ["read"]
        raw_key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        record = ApiKey(
            workspace_id=ws_id,
            name=name,
            key_hash=key_hash,
            key_prefix=raw_key[:12],
            permissions=permissions,
            rate_limit=1000,
            is_active=True,
        )
        record.save()
        data = serialize_doc(record) or {}
        data.pop("key_hash", None)
        data["api_key"] = raw_key
        return Response(data, status=status.HTTP_201_CREATED)


class ApiKeyRevokeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_WORKSPACE.value)]

    def delete(self, request, key_id):
        ws_id = get_workspace_id(request)
        key = ApiKey.objects(id=key_id, workspace_id=ws_id).first()
        if not key:
            return Response({"detail": "API key not found"}, status=status.HTTP_404_NOT_FOUND)
        key.delete()
        return Response({"message": "API key revoked"})
