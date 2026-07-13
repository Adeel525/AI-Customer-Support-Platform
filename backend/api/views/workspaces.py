"""
Workspace API views — current workspace, branding, members.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id, require_member
from api.models import User, Workspace, WorkspaceMember, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from api.serializers import BrandingUpdateSerializer, MemberInviteSerializer, WorkspaceUpdateSerializer
from core.enums import Permission, UserRole
from core.utils.email_service import EmailService


class CurrentWorkspaceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT]

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [
                IsAuthenticatedJWT(),
                HasWorkspacePermission(Permission.MANAGE_WORKSPACE.value)(),
            ]
        return [IsAuthenticatedJWT()]

    def get(self, request):
        ws_id = get_workspace_id(request)
        if not ws_id:
            return Response({"detail": "Workspace ID required"}, status=status.HTTP_400_BAD_REQUEST)
        require_member(request.user.id, ws_id)
        ws = Workspace.objects(id=ws_id).first()
        if not ws:
            return Response({"detail": "Workspace not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_doc(ws))

    def patch(self, request):
        ws_id = get_workspace_id(request)
        ws = Workspace.objects(id=ws_id).first()
        if not ws:
            return Response({"detail": "Workspace not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = WorkspaceUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        if "name" in data:
            ws.name = data["name"]

        settings_keys = ("support_email", "business_hours", "categories", "language", "custom_domain")
        settings_update = {k: data[k] for k in settings_keys if k in data}
        if settings_update:
            current = dict(ws.settings or {})
            current.update(settings_update)
            ws.settings = current

        ws.save()
        return Response(serialize_doc(ws))


class BrandingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_WORKSPACE.value)]

    def patch(self, request):
        ws_id = get_workspace_id(request)
        ws = Workspace.objects(id=ws_id).first()
        if not ws:
            return Response({"detail": "Workspace not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = BrandingUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        branding = dict(ws.branding or {})
        branding.update({k: v for k, v in ser.validated_data.items() if v is not None})
        ws.branding = branding
        ws.save()
        return Response(serialize_doc(ws))


class MembersListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT]

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticatedJWT(),
                HasWorkspacePermission(Permission.MANAGE_MEMBERS.value)(),
            ]
        return [IsAuthenticatedJWT()]

    def get(self, request):
        ws_id = get_workspace_id(request)
        if not ws_id:
            return Response({"detail": "Workspace ID required"}, status=status.HTTP_400_BAD_REQUEST)
        require_member(request.user.id, ws_id)

        members = WorkspaceMember.objects(workspace_id=ws_id)
        result = []
        for m in members:
            user = User.objects(id=m.user_id).first()
            item = serialize_doc(m)
            if user:
                item["user"] = {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "is_verified": bool(user.is_verified),
                }
            result.append(item)
        return Response({"items": result, "total": len(result)})

    def post(self, request):
        ws_id = get_workspace_id(request)
        ser = MemberInviteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower().strip()
        role = ser.validated_data["role"]

        if role == UserRole.OWNER.value:
            return Response({"detail": "Cannot invite as owner"}, status=status.HTTP_400_BAD_REQUEST)

        ws = Workspace.objects(id=ws_id).first()
        if not ws:
            return Response({"detail": "Workspace not found"}, status=status.HTTP_404_NOT_FOUND)

        user = User.objects(email=email).first()
        inviter_name = getattr(request.user, "full_name", None) or "Admin"

        if user:
            existing = WorkspaceMember.objects(workspace_id=ws_id, user_id=str(user.id)).first()
            if existing:
                return Response({"detail": "Already a member"}, status=status.HTTP_400_BAD_REQUEST)
            member = WorkspaceMember(
                workspace_id=ws_id,
                user_id=str(user.id),
                role=role,
            )
            member.save()
            return Response(serialize_doc(member), status=status.HTTP_201_CREATED)

        EmailService().send_invite_email(email, ws.name, inviter_name)
        return Response(
            {"email": email, "status": "invited", "role": role},
            status=status.HTTP_201_CREATED,
        )


class MemberDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_MEMBERS.value)]

    def patch(self, request, user_id):
        ws_id = get_workspace_id(request)
        role = request.data.get("role")
        if not role:
            return Response({"detail": "role is required"}, status=status.HTTP_400_BAD_REQUEST)
        if role == UserRole.OWNER.value:
            return Response({"detail": "Cannot assign owner role"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            UserRole(role)
        except ValueError:
            return Response({"detail": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        member = WorkspaceMember.objects(workspace_id=ws_id, user_id=str(user_id)).first()
        if not member:
            return Response({"detail": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        if member.role == UserRole.OWNER.value:
            return Response({"detail": "Cannot change owner role"}, status=status.HTTP_400_BAD_REQUEST)

        member.role = role
        member.save()
        return Response(serialize_doc(member))

    def delete(self, request, user_id):
        ws_id = get_workspace_id(request)
        member = WorkspaceMember.objects(workspace_id=ws_id, user_id=str(user_id)).first()
        if not member:
            return Response({"detail": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        if member.role == UserRole.OWNER.value:
            return Response({"detail": "Cannot remove owner"}, status=status.HTTP_400_BAD_REQUEST)

        member.delete()
        return Response({"message": "Member removed"})
