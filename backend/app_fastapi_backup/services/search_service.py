from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import VectorStore
from app.repositories.document_repository import DocumentChunkRepository
from app.repositories.ticket_repository import TicketRepository


class SearchService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStore()
        self.chunk_repo = DocumentChunkRepository(db, workspace_id)
        self.ticket_repo = TicketRepository(db, workspace_id)

    async def semantic_search(self, query: str, entity_types: list[str] | None = None) -> dict:
        query_vector = await self.embeddings.embed_text(query)
        vector_results = await self.vector_store.search(
            self.workspace_id, query_vector, top_k=10
        )
        keyword_results = await self.chunk_repo.keyword_search(query, limit=5)

        results = {
            "documents": [],
            "tickets": [],
        }

        for r in vector_results:
            meta = r.get("metadata", {})
            results["documents"].append({
                "id": r["id"],
                "score": r["score"],
                "content": meta.get("content", "")[:300],
                "source": meta.get("source", ""),
            })

        if not entity_types or "tickets" in entity_types:
            tickets, _ = await self.ticket_repo.list(limit=100)
            for ticket in tickets:
                if query.lower() in ticket.get("title", "").lower() or query.lower() in ticket.get("description", "").lower():
                    results["tickets"].append({
                        "id": ticket["id"],
                        "title": ticket["title"],
                        "status": ticket["status"],
                    })

        return results
