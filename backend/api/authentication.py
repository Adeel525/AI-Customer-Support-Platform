"""
Custom DRF JWT authentication and tenant helpers for mongoengine users.
"""
from __future__ import annotations

from typing import Any

from bson.errors import InvalidId
from rest_framework import authentication, exceptions
from rest_framework.exceptions import PermissionDenied

from api.jwt_utils import decode_token
from api.models import User, WorkspaceMember
from core.enums import ROLE_PERMISSIONS, Permission, UserRole


class UserProxy:
    """Lightweight authenticated user object attached to request.user."""

    is_authenticated = True
    is_anonymous = False

    def __init__(
        self,
        *,
        id: str,
        email: str,
        full_name: str,
        is_verified: bool = False,
        avatar_url: str | None = None,
        oauth_provider: str | None = None,
    ):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.is_verified = is_verified
        self.avatar_url = avatar_url
        self.oauth_provider = oauth_provider

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_verified": self.is_verified,
            "avatar_url": self.avatar_url,
            "oauth_provider": self.oauth_provider,
        }

    def __str__(self) -> str:
        return self.email or self.id


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests via Bearer JWT (PyJWT + Django SECRET_KEY).

    Validates token type == "access", loads the mongoengine User, and returns
    (UserProxy, raw_token).
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) == 0:
            return None
        if parts[0] != self.keyword:
            return None
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format")

        token = parts[1]
        payload = decode_token(token)
        if not payload:
            raise exceptions.AuthenticationFailed("Invalid or expired token")
        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("Invalid token payload")

        try:
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, InvalidId, ValueError):
            raise exceptions.AuthenticationFailed("User not found") from None

        proxy = UserProxy(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            is_verified=bool(user.is_verified),
            avatar_url=user.avatar_url,
            oauth_provider=user.oauth_provider,
        )
        # Attach decoded claims for tenant helpers
        request.jwt_payload = payload  # type: ignore[attr-defined]
        return (proxy, token)

    def authenticate_header(self, request) -> str:
        return self.keyword


class TenantMixin:
    """Optional mixin for views that need workspace-scoped access."""

    workspace_header = "HTTP_X_WORKSPACE_ID"

    def get_workspace_id(self, request) -> str | None:
        return get_workspace_id(request)

    def require_member(self, request) -> WorkspaceMember:
        user = getattr(request, "user", None)
        user_id = getattr(user, "id", None)
        workspace_id = get_workspace_id(request)
        if not user_id or not workspace_id:
            raise PermissionDenied("Workspace membership required")
        return require_member(user_id, workspace_id)


def get_workspace_id(request) -> str | None:
    """Resolve workspace id from X-Workspace-Id header or JWT claim."""
    header_value = request.headers.get("X-Workspace-Id") or request.META.get("HTTP_X_WORKSPACE_ID")
    if header_value:
        return str(header_value).strip() or None

    payload = getattr(request, "jwt_payload", None)
    if isinstance(payload, dict) and payload.get("workspace_id"):
        return str(payload["workspace_id"])

    # Fallback: decode Bearer token if authentication did not run yet
    auth_header = authentication.get_authorization_header(request).decode("utf-8")
    parts = auth_header.split()
    if len(parts) == 2 and parts[0] == "Bearer":
        payload = decode_token(parts[1])
        if payload and payload.get("workspace_id"):
            return str(payload["workspace_id"])

    return None


def require_member(user_id: str, workspace_id: str) -> WorkspaceMember:
    """Return WorkspaceMember or raise PermissionDenied."""
    member = WorkspaceMember.objects(
        workspace_id=str(workspace_id),
        user_id=str(user_id),
    ).first()
    if not member:
        raise PermissionDenied("Not a workspace member")
    return member


def has_permission(role: str, permission: str) -> bool:
    """Check whether a role grants the given permission via ROLE_PERMISSIONS."""
    try:
        role_enum = UserRole(role)
    except ValueError:
        return False

    try:
        perm_enum = Permission(permission)
    except ValueError:
        return False

    allowed = ROLE_PERMISSIONS.get(role_enum, set())
    return perm_enum in allowed
