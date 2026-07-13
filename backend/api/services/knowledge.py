"""
Sync knowledge-base document processing (extract → chunk → embed → upsert).
"""
from __future__ import annotations

import logging

from api.models import Document, DocumentChunk, serialize_doc
from core.ai.embeddings import EmbeddingService
from core.ai.vector_store import VectorStore
from core.enums import DocumentStatus
from core.utils.chunking import estimate_tokens, split_text
from core.utils.document_processor import extract_document
from core.utils.storage import StorageService

logger = logging.getLogger(__name__)


def process_document(document_id: str, workspace_id: str) -> dict:
    """
    Process a pending document synchronously:
    download → extract text → chunk → embed → Pinecone upsert → save chunks.
    """
    doc = Document.objects(id=document_id, workspace_id=workspace_id).first()
    if not doc:
        raise ValueError("Document not found")

    doc.status = DocumentStatus.PROCESSING.value
    doc.error = None
    doc.save()

    storage = StorageService()
    embeddings = EmbeddingService()
    vector_store = VectorStore()

    try:
        content = storage.download_file(doc.s3_key)
        text, page_count = extract_document(content, doc.filename)
        chunks = split_text(text)
        total_tokens = 0
        vectors = []

        # Clear prior chunks if re-processing
        DocumentChunk.objects(document_id=document_id, workspace_id=workspace_id).delete()

        for i, chunk_text in enumerate(chunks):
            chunk_id = VectorStore.generate_chunk_id()
            token_count = estimate_tokens(chunk_text)
            total_tokens += token_count

            embedding = embeddings.embed_text(chunk_text)
            metadata = {
                "chunk_id": chunk_id,
                "workspace_id": workspace_id,
                "document_id": document_id,
                "page_number": min(i + 1, max(page_count, 1)),
                "source": doc.filename,
                "content": chunk_text,
                "token_count": token_count,
                "embedding_model": "text-embedding-3-small",
            }

            DocumentChunk(
                workspace_id=workspace_id,
                document_id=document_id,
                chunk_id=chunk_id,
                content=chunk_text,
                page_number=metadata["page_number"],
                source=doc.filename,
                token_count=token_count,
                embedding_model="text-embedding-3-small",
            ).save()

            vectors.append((chunk_id, embedding, metadata))

        if vectors:
            vector_store.upsert(workspace_id, vectors)

        doc.status = DocumentStatus.INDEXED.value
        doc.token_count = total_tokens
        doc.page_count = page_count
        doc.chunk_count = len(chunks)
        doc.error = None
        doc.save()
        return serialize_doc(doc)

    except Exception as exc:
        logger.exception("Failed to process document %s", document_id)
        doc.status = DocumentStatus.FAILED.value
        doc.error = str(exc)
        doc.save()
        raise


def ingest_text(workspace_id: str, title: str, content: str, source: str = "crawler") -> dict:
    """Upload plain text as a document and process it inline."""
    storage = StorageService()
    s3_key = storage.upload_file(workspace_id, f"{title}.txt", content.encode("utf-8"))
    doc = Document(
        workspace_id=workspace_id,
        filename=title,
        file_type=".txt",
        s3_key=s3_key,
        status=DocumentStatus.PENDING.value,
        source=source,
        file_size=len(content.encode("utf-8")),
    )
    doc.save()
    return process_document(str(doc.id), workspace_id)
