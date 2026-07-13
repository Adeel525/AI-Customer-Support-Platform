"""
DRF permission classes for JWT + workspace RBAC.
"""
from __future__ import annotations

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from api.authentication import get_workspace_id, has_permission, require_member
from core.enums import UserRole


class IsAuthenticatedJWT(BasePermission):
    """Require a successful JWTAuthentication (UserProxy on request.user)."""

    message = "Authentication credentials were not provided or are invalid."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False) and getattr(user, "id", None))


def HasWorkspacePermission(permission: str):
    """
    Factory returning a permission class that checks workspace membership
    and role-based permission against core.enums.ROLE_PERMISSIONS.
    """

    class _HasWorkspacePermission(BasePermission):
        message = f"Permission denied: {permission}"

        def has_permission(self, request, view) -> bool:
            user = getattr(request, "user", None)
            user_id = getattr(user, "id", None)
            if not user_id:
                return False

            workspace_id = get_workspace_id(request)
            if not workspace_id:
                self.message = "Workspace ID required (X-Workspace-Id header or token claim)"
                return False

            try:
                member = require_member(user_id, workspace_id)
            except PermissionDenied:
                self.message = "Not a workspace member"
                return False

            request.workspace_id = workspace_id  # type: ignore[attr-defined]
            request.workspace_member = member  # type: ignore[attr-defined]
            request.workspace_role = member.role  # type: ignore[attr-defined]

            if not has_permission(member.role, permission):
                self.message = f"Permission denied: {permission}"
                return False
            return True

    _HasWorkspacePermission.__name__ = f"HasWorkspacePermission_{permission}"
    return _HasWorkspacePermission


class IsOwnerOrAdmin(BasePermission):
    """Allow only workspace owners and admins."""

    message = "Owner or admin role required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        user_id = getattr(user, "id", None)
        if not user_id:
            return False

        workspace_id = get_workspace_id(request)
        if not workspace_id:
            self.message = "Workspace ID required (X-Workspace-Id header or token claim)"
            return False

        try:
            member = require_member(user_id, workspace_id)
        except PermissionDenied:
            self.message = "Not a workspace member"
            return False

        request.workspace_id = workspace_id  # type: ignore[attr-defined]
        request.workspace_member = member  # type: ignore[attr-defined]
        request.workspace_role = member.role  # type: ignore[attr-defined]

        try:
            role = UserRole(member.role)
        except ValueError:
            return False

        return role in {UserRole.OWNER, UserRole.ADMIN}
