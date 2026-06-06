from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    collection_name = "documents"


class DocumentChunkRepository(BaseRepository):
    collection_name = "document_chunks"

    async def delete_by_document(self, document_id: str) -> int:
        result = await self.collection.delete_many(
            self._base_filter({"document_id": document_id})
        )
        return result.deleted_count

    async def keyword_search(self, query: str, limit: int = 10) -> list[dict]:
        cursor = self.collection.find(
            self._base_filter({"content": {"$regex": query, "$options": "i"}})
        ).limit(limit)
        docs = await cursor.to_list(limit)
        return self._serialize_many(docs)
