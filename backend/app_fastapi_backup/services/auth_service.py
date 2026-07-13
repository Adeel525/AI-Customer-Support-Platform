import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.utils.email_service import EmailService


class AuthService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.member_repo = WorkspaceMemberRepository(db)
        self.email_service = EmailService()

    async def signup(self, email: str, password: str, full_name: str, workspace_name: str) -> dict:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        verification_token = generate_token()
        auto_verify = not self.email_service.enabled

        user = await self.user_repo.create({
            "email": email,
            "password_hash": hash_password(password),
            "full_name": full_name,
            "is_verified": auto_verify,
            "verification_token": verification_token,
            "oauth_provider": None,
        })

        slug = self._generate_slug(workspace_name)
        workspace = await self.workspace_repo.create({
            "name": workspace_name,
            "slug": slug,
            "branding": {},
            "settings": {"language": "en", "categories": []},
            "plan": "free",
        })

        await self.member_repo.create({
            "workspace_id": workspace["id"],
            "user_id": user["id"],
            "role": UserRole.OWNER.value,
        })

        if not auto_verify:
            await self.email_service.send_verification_email(email, verification_token)

        tokens = self._create_tokens(user["id"], workspace["id"], UserRole.OWNER.value)
        return {"user": user, "workspace": workspace, **tokens}

    async def login(self, email: str, password: str, workspace_id: str | None = None) -> dict:
        user_doc = await self.user_repo.collection.find_one({"email": email.lower()})
        if not user_doc or not verify_password(password, user_doc.get("password_hash", "")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        user = await self.user_repo.get_by_id(str(user_doc["_id"]))
        members = await self.member_repo.list_by_user(user["id"])
        if not members:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No workspace membership")

        member = members[0]
        if workspace_id:
            member = next((m for m in members if m["workspace_id"] == workspace_id), member)

        tokens = self._create_tokens(user["id"], member["workspace_id"], member["role"])
        return {"user": user, **tokens}

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = payload.get("sub")
        members = await self.member_repo.list_by_user(user_id)
        if not members:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No workspace")

        member = members[0]
        return self._create_tokens(user_id, member["workspace_id"], member["role"])

    async def verify_email(self, token: str) -> bool:
        doc = await self.user_repo.collection.find_one({"verification_token": token})
        if not doc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        await self.user_repo.update(str(doc["_id"]), {
            "is_verified": True,
            "verification_token": None,
        })
        return True

    async def forgot_password(self, email: str) -> bool:
        user_doc = await self.user_repo.collection.find_one({"email": email.lower()})
        if not user_doc:
            return True
        token = generate_token()
        await self.user_repo.update(str(user_doc["_id"]), {
            "reset_token": token,
            "reset_token_expires": datetime.now(timezone.utc) + timedelta(hours=1),
        })
        await self.email_service.send_password_reset_email(email, token)
        return True

    async def reset_password(self, token: str, new_password: str) -> bool:
        doc = await self.user_repo.collection.find_one({
            "reset_token": token,
            "reset_token_expires": {"$gt": datetime.now(timezone.utc)},
        })
        if not doc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
        await self.user_repo.update(str(doc["_id"]), {
            "password_hash": hash_password(new_password),
            "reset_token": None,
            "reset_token_expires": None,
        })
        return True

    async def get_me(self, user_id: str) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        members = await self.member_repo.list_by_user(user_id)
        workspaces = []
        for m in members:
            ws = await self.workspace_repo.get_by_id(m["workspace_id"])
            if ws:
                workspaces.append({**ws, "role": m["role"]})
        return {"user": user, "workspaces": workspaces}

    async def handle_oauth_user(self, email: str, full_name: str, provider: str) -> dict:
        user_doc = await self.user_repo.collection.find_one({"email": email.lower()})
        if user_doc:
            user = await self.user_repo.get_by_id(str(user_doc["_id"]))
            members = await self.member_repo.list_by_user(user["id"])
            member = members[0] if members else None
            if not member:
                workspace = await self._create_default_workspace(user["id"], full_name)
                member = {"workspace_id": workspace["id"], "role": UserRole.OWNER.value}
            tokens = self._create_tokens(user["id"], member["workspace_id"], member["role"])
            return {"user": user, **tokens}

        user = await self.user_repo.create({
            "email": email,
            "full_name": full_name,
            "is_verified": True,
            "oauth_provider": provider,
            "password_hash": None,
        })
        workspace = await self._create_default_workspace(user["id"], f"{full_name}'s Workspace")
        tokens = self._create_tokens(user["id"], workspace["id"], UserRole.OWNER.value)
        return {"user": user, **tokens}

    async def _create_default_workspace(self, user_id: str, name: str) -> dict:
        workspace = await self.workspace_repo.create({
            "name": name,
            "slug": self._generate_slug(name),
            "branding": {},
            "settings": {},
            "plan": "free",
        })
        await self.member_repo.create({
            "workspace_id": workspace["id"],
            "user_id": user_id,
            "role": UserRole.OWNER.value,
        })
        return workspace

    def _create_tokens(self, user_id: str, workspace_id: str, role: str) -> dict:
        return {
            "access_token": create_access_token(user_id, workspace_id, role),
            "refresh_token": create_refresh_token(user_id),
            "token_type": "bearer",
        }

    def _generate_slug(self, name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        return slug[:50] or "workspace"
