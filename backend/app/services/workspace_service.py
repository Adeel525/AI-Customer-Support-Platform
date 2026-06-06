from fastapi import HTTPException, status

from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.utils.email_service import EmailService


class WorkspaceService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.workspace_repo = WorkspaceRepository(db, workspace_id)
        self.member_repo = WorkspaceMemberRepository(db)
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()

    async def get_workspace(self) -> dict:
        ws = await self.workspace_repo.get_by_id(self.workspace_id)
        if not ws:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        return ws

    async def update_workspace(self, data: dict) -> dict:
        return await self.workspace_repo.update(self.workspace_id, data)

    async def update_branding(self, data: dict) -> dict:
        ws = await self.get_workspace()
        branding = {**ws.get("branding", {}), **{k: v for k, v in data.items() if v is not None}}
        return await self.workspace_repo.update(self.workspace_id, {"branding": branding})

    async def list_members(self) -> list[dict]:
        members = await self.member_repo.list_by_workspace(self.workspace_id)
        result = []
        for m in members:
            user = await self.user_repo.get_by_id(m["user_id"])
            if user:
                result.append({**m, "user": user})
        return result

    async def invite_member(self, email: str, role: str, inviter_name: str) -> dict:
        if role == UserRole.OWNER.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot invite as owner")

        user_doc = await self.user_repo.collection.find_one({"email": email.lower()})
        ws = await self.get_workspace()

        if user_doc:
            existing = await self.member_repo.get_member(self.workspace_id, str(user_doc["_id"]))
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member")
            member = await self.member_repo.create({
                "workspace_id": self.workspace_id,
                "user_id": str(user_doc["_id"]),
                "role": role,
            })
        else:
            await self.email_service.send_invite_email(email, ws["name"], inviter_name)
            member = {"email": email, "status": "invited", "role": role}

        return member

    async def update_member_role(self, user_id: str, role: str) -> dict:
        if role == UserRole.OWNER.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign owner role")
        return await self.member_repo.update_role(self.workspace_id, user_id, role)

    async def remove_member(self, user_id: str) -> bool:
        member = await self.member_repo.get_member(self.workspace_id, user_id)
        if member and member["role"] == UserRole.OWNER.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove owner")
        return await self.member_repo.delete(self.workspace_id, user_id)
