import hashlib
import secrets

from fastapi import HTTPException, status

from app.repositories.api_key_repository import ApiKeyRepository


class ApiPlatformService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.repo = ApiKeyRepository(db, workspace_id)

    async def create_api_key(self, name: str, permissions: list[str] | None = None) -> dict:
        raw_key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        record = await self.repo.create({
            "name": name,
            "key_hash": key_hash,
            "key_prefix": raw_key[:12],
            "permissions": permissions or ["read"],
            "rate_limit": 1000,
            "is_active": True,
        })
        return {**record, "api_key": raw_key}

    async def list_api_keys(self) -> list:
        items, _ = await self.repo.list()
        return [{k: v for k, v in item.items() if k != "key_hash"} for item in items]

    async def revoke_api_key(self, key_id: str) -> bool:
        return await self.repo.delete(key_id)

    async def validate_api_key(self, raw_key: str) -> dict | None:
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return await self.repo.get_by_hash(key_hash)
