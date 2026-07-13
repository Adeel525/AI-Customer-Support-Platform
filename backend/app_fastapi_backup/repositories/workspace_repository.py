from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository):
    collection_name = "workspaces"

    async def get_by_slug(self, slug: str) -> dict | None:
        doc = await self.collection.find_one({"slug": slug})
        return self._serialize(doc)
