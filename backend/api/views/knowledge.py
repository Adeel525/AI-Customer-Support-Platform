"""
Knowledge base API views — document upload, list, delete, stats.
"""
from __future__ import annotations

import logging
from pathlib import Path

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import Document, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from api.services.knowledge import process_document
from core.enums import DocumentStatus, Permission
from core.utils.storage import StorageService

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".html", ".htm"}


def _queue_or_process(document_id: str, workspace_id: str) -> None:
    """Try Celery task; fall back to sync processing."""
    try:
        from api.tasks import process_document as process_document_task

        process_document_task.delay(document_id, workspace_id)
        return
    except Exception:
        pass

    try:
        process_document(document_id, workspace_id)
    except Exception:
        logger.exception("Inline document processing failed for %s", document_id)


class DocumentUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_KNOWLEDGE.value)]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        ws_id = get_workspace_id(request)
        uploaded = request.FILES.get("file")
        if not uploaded:
            return Response({"detail": "file is required"}, status=status.HTTP_400_BAD_REQUEST)

        filename = uploaded.name or "document"
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {"detail": f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content = uploaded.read()
        storage = StorageService()
        s3_key = storage.upload_file(ws_id, filename, content)

        doc = Document(
            workspace_id=ws_id,
            filename=filename,
            file_type=ext,
            s3_key=s3_key,
            status=DocumentStatus.PENDING.value,
            token_count=0,
            page_count=0,
            source="upload",
            file_size=len(content),
        )
        doc.save()

        _queue_or_process(str(doc.id), ws_id)
        # Reload in case sync processing updated it
        doc.reload()
        return Response(serialize_doc(doc), status=status.HTTP_201_CREATED)


class DocumentListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_KNOWLEDGE.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        try:
            skip = int(request.query_params.get("skip", 0))
            limit = int(request.query_params.get("limit", 50))
        except (TypeError, ValueError):
            skip, limit = 0, 50
        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        qs = Document.objects(workspace_id=ws_id).order_by("-created_at")
        total = qs.count()
        items = [serialize_doc(d) for d in qs.skip(skip).limit(limit)]
        return Response({
            "items": items,
            "total": total,
            "page": skip // limit + 1 if limit else 1,
            "page_size": limit,
        })


class DocumentDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_KNOWLEDGE.value)]

    def delete(self, request, document_id):
        ws_id = get_workspace_id(request)
        doc = Document.objects(id=document_id, workspace_id=ws_id).first()
        if not doc:
            return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        storage = StorageService()
        if doc.s3_key:
            storage.delete_file(doc.s3_key)

        try:
            from core.ai.vector_store import VectorStore
            from api.models import DocumentChunk

            VectorStore().delete_by_document(ws_id, document_id)
            DocumentChunk.objects(document_id=document_id, workspace_id=ws_id).delete()
        except Exception:
            logger.exception("Failed to clean vectors/chunks for %s", document_id)

        doc.delete()
        return Response({"message": "Document deleted"})


class KnowledgeStatsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_KNOWLEDGE.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        docs = list(Document.objects(workspace_id=ws_id))
        total = len(docs)
        tokens = sum(d.token_count or 0 for d in docs)
        pages = sum(d.page_count or 0 for d in docs)
        indexed = sum(1 for d in docs if d.status == DocumentStatus.INDEXED.value)
        last_sync = None
        for d in docs:
            if d.updated_at and (last_sync is None or d.updated_at > last_sync):
                last_sync = d.updated_at

        return Response({
            "total_documents": total,
            "pages_indexed": pages,
            "tokens_indexed": tokens,
            "indexed_documents": indexed,
            "last_sync_time": last_sync.isoformat() if last_sync else None,
            "coverage_score": round(indexed / max(total, 1) * 100, 1),
        })
