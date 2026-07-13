import logging
import uuid
from typing import Any

from core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Pinecone vector store with in-memory fallback."""

    def __init__(self):
        self._memory_store: dict[str, dict[str, list[tuple[str, list[float], dict]]]] = {}
        self._pinecone = None
        self._index = None
        if settings.PINECONE_API_KEY:
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                self._index = pc.Index(settings.PINECONE_INDEX_NAME)
                self._pinecone = pc
            except Exception as e:
                logger.warning("Pinecone init failed, using memory store: %s", e)

    def _namespace(self, workspace_id: str) -> str:
        return f"workspace_{workspace_id}"

    def upsert(
        self,
        workspace_id: str,
        vectors: list[tuple[str, list[float], dict[str, Any]]],
    ) -> int:
        namespace = self._namespace(workspace_id)
        if self._index:
            records = [
                {"id": vid, "values": vec, "metadata": {**meta, "content": meta.get("content", "")[:1000]}}
                for vid, vec, meta in vectors
            ]
            self._index.upsert(vectors=records, namespace=namespace)
            return len(records)

        if namespace not in self._memory_store:
            self._memory_store[namespace] = {}
        for vid, vec, meta in vectors:
            self._memory_store[namespace][vid] = (vid, vec, meta)
        return len(vectors)

    def search(
        self,
        workspace_id: str,
        query_vector: list[float],
        top_k: int = 20,
        filter_meta: dict | None = None,
    ) -> list[dict]:
        namespace = self._namespace(workspace_id)
        if self._index:
            results = self._index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True,
                filter=filter_meta,
            )
            return [
                {
                    "id": m.id,
                    "score": m.score,
                    "metadata": m.metadata or {},
                }
                for m in results.matches
            ]

        ns = self._memory_store.get(namespace, {})
        scored = []
        for vid, (_, vec, meta) in ns.items():
            score = self._cosine_similarity(query_vector, vec)
            if filter_meta:
                if not all(meta.get(k) == v for k, v in filter_meta.items()):
                    continue
            scored.append({"id": vid, "score": score, "metadata": meta})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete_by_document(self, workspace_id: str, document_id: str) -> None:
        namespace = self._namespace(workspace_id)
        if self._index:
            self._index.delete(filter={"document_id": document_id}, namespace=namespace)
            return
        ns = self._memory_store.get(namespace, {})
        to_delete = [k for k, (_, _, m) in ns.items() if m.get("document_id") == document_id]
        for k in to_delete:
            del ns[k]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def generate_chunk_id() -> str:
        return str(uuid.uuid4())
