"""
Auth API views — signup, login, refresh, me, email verify, password reset, Google OAuth stubs.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication
from api.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_token,
    hash_password,
    verify_password,
)
from api.models import User, Workspace, WorkspaceMember, serialize_doc
from api.permissions import IsAuthenticatedJWT
from api.serializers import LoginSerializer, RefreshSerializer, SignupSerializer
from core.enums import UserRole
from core.utils.email_service import EmailService


def _tokens(user_id: str, workspace_id: str, role: str) -> dict:
    return {
        "access_token": create_access_token(user_id, workspace_id, role),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }


def _public_user(user: User) -> dict:
    data = user.to_dict()
    data.pop("verification_token", None)
    data.pop("reset_token", None)
    data.pop("reset_token_expires", None)
    data.pop("password_hash", None)
    return data


def _generate_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = slug[:50] or "workspace"
    base = slug
    counter = 1
    while Workspace.objects(slug=slug).first():
        suffix = f"-{counter}"
        slug = f"{base[: 50 - len(suffix)]}{suffix}"
        counter += 1
    return slug


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = SignupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        email = data["email"].lower().strip()
        if User.objects(email=email).first():
            return Response({"detail": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        email_service = EmailService()
        auto_verify = not email_service.enabled
        verification_token = generate_token()

        user = User(
            email=email,
            password_hash=hash_password(data["password"]),
            full_name=data["full_name"],
            is_verified=auto_verify,
            verification_token=None if auto_verify else verification_token,
        )
        user.save()

        workspace = Workspace(
            name=data["workspace_name"],
            slug=_generate_slug(data["workspace_name"]),
            branding={},
            settings={"language": "en", "categories": []},
            plan="free",
        )
        workspace.save()

        WorkspaceMember(
            workspace_id=str(workspace.id),
            user_id=str(user.id),
            role=UserRole.OWNER.value,
        ).save()

        if not auto_verify:
            email_service.send_verification_email(email, verification_token)

        tokens = _tokens(str(user.id), str(workspace.id), UserRole.OWNER.value)
        return Response(
            {
                "user": _public_user(user),
                "workspace": serialize_doc(workspace),
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        email = data["email"].lower().strip()
        user = User.objects(email=email).first()
        if not user or not verify_password(data["password"], user.password_hash or ""):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        members = list(WorkspaceMember.objects(user_id=str(user.id)))
        if not members:
            return Response({"detail": "No workspace membership"}, status=status.HTTP_403_FORBIDDEN)

        member = members[0]
        workspace_id = data.get("workspace_id")
        if workspace_id:
            member = next(
                (m for m in members if m.workspace_id == workspace_id),
                member,
            )

        tokens = _tokens(str(user.id), member.workspace_id, member.role)
        return Response({"user": _public_user(user), **tokens})


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RefreshSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        payload = decode_token(ser.validated_data["refresh_token"])
        if not payload or payload.get("type") != "refresh":
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload.get("sub")
        members = list(WorkspaceMember.objects(user_id=str(user_id)))
        if not members:
            return Response({"detail": "No workspace"}, status=status.HTTP_403_FORBIDDEN)

        member = members[0]
        return Response(_tokens(user_id, member.workspace_id, member.role))


class MeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT]

    def get(self, request):
        user = User.objects(id=request.user.id).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        members = list(WorkspaceMember.objects(user_id=str(user.id)))
        workspaces = []
        for m in members:
            ws = Workspace.objects(id=m.workspace_id).first()
            if ws:
                ws_data = serialize_doc(ws)
                ws_data["role"] = m.role
                workspaces.append(ws_data)

        return Response({"user": _public_user(user), "workspaces": workspaces})


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"detail": "token is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects(verification_token=token).first()
        if not user:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.verification_token = None
        user.save()
        return Response({"message": "Email verified successfully"})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").lower().strip()
        if not email:
            return Response({"detail": "email is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects(email=email).first()
        if user:
            token = generate_token()
            user.reset_token = token
            user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
            user.save()
            EmailService().send_password_reset_email(email, token)

        return Response({"message": "If the email exists, a reset link has been sent"})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        if not token or not new_password:
            return Response(
                {"detail": "token and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_password) < 8:
            return Response(
                {"detail": "Password must be at least 8 characters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects(reset_token=token).first()
        if not user or not user.reset_token_expires:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        expires = user.reset_token_expires
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.save()
        return Response({"message": "Password reset successfully"})


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "") or ""
        if not client_id:
            return Response({"error": "Google OAuth not configured"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "message": "Google OAuth needs configuration. Use authorization code flow with GOOGLE_CLIENT_ID.",
                "redirect_uri": getattr(settings, "GOOGLE_REDIRECT_URI", ""),
            }
        )


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {"detail": "Google OAuth callback not fully configured"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
