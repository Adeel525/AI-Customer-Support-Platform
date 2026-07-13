"""
Semantic search API view.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import DocumentChunk, Ticket
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from core.ai.embeddings import EmbeddingService
from core.ai.vector_store import VectorStore
from core.enums import Permission


class SearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_KNOWLEDGE.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        query = (request.query_params.get("q") or "").strip()
        if not query:
            return Response({"detail": "q is required"}, status=status.HTTP_400_BAD_REQUEST)

        entity_types = request.query_params.get("entity_types")
        types = [t.strip() for t in entity_types.split(",")] if entity_types else None

        embeddings = EmbeddingService()
        vector_store = VectorStore()
        query_vector = embeddings.embed_text(query)
        vector_results = vector_store.search(ws_id, query_vector, top_k=10)

        results = {"documents": [], "tickets": []}

        for r in vector_results:
            meta = r.get("metadata") or {}
            results["documents"].append({
                "id": r.get("id"),
                "score": r.get("score"),
                "content": (meta.get("content") or "")[:300],
                "source": meta.get("source", ""),
            })

        # Keyword boost from chunks
        for chunk in DocumentChunk.objects(workspace_id=ws_id, content__icontains=query[:100])[:5]:
            results["documents"].append({
                "id": chunk.chunk_id,
                "score": 0.5,
                "content": (chunk.content or "")[:300],
                "source": chunk.source or "",
            })

        if not types or "tickets" in types:
            q_lower = query.lower()
            for ticket in Ticket.objects(workspace_id=ws_id).limit(100):
                title = (ticket.title or "").lower()
                desc = (ticket.description or "").lower()
                if q_lower in title or q_lower in desc:
                    results["tickets"].append({
                        "id": str(ticket.id),
                        "title": ticket.title,
                        "status": ticket.status,
                    })

        return Response(results)
