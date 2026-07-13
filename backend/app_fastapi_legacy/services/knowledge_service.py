from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import VectorStore
from app.models.enums import DocumentStatus
from app.repositories.document_repository import DocumentChunkRepository, DocumentRepository
from app.utils.chunking import estimate_tokens, split_text
from app.utils.document_processor import extract_document
from app.utils.storage import StorageService


class KnowledgeService:
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".html", ".htm"}

    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.doc_repo = DocumentRepository(db, workspace_id)
        self.chunk_repo = DocumentChunkRepository(db, workspace_id)
        self.storage = StorageService()
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStore()

    async def upload_document(self, file: UploadFile) -> dict:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}",
            )

        content = await file.read()
        s3_key = await self.storage.upload_file(self.workspace_id, file.filename or "document", content)

        doc = await self.doc_repo.create({
            "filename": file.filename,
            "file_type": ext,
            "s3_key": s3_key,
            "status": DocumentStatus.PENDING.value,
            "token_count": 0,
            "page_count": 0,
            "source": "upload",
            "file_size": len(content),
        })

        from app.workers.ingestion_tasks import process_document
        process_document.delay(doc["id"], self.workspace_id)

        return doc

    async def process_document(self, document_id: str) -> dict:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        await self.doc_repo.update(document_id, {"status": DocumentStatus.PROCESSING.value})

        try:
            content = await self.storage.download_file(doc["s3_key"])
            text, page_count = extract_document(content, doc["filename"])
            chunks = split_text(text)
            total_tokens = 0
            vectors = []

            for i, chunk_text in enumerate(chunks):
                chunk_id = VectorStore.generate_chunk_id()
                token_count = estimate_tokens(chunk_text)
                total_tokens += token_count

                embedding = await self.embeddings.embed_text(chunk_text)
                metadata = {
                    "chunk_id": chunk_id,
                    "workspace_id": self.workspace_id,
                    "document_id": document_id,
                    "page_number": min(i + 1, page_count),
                    "source": doc["filename"],
                    "content": chunk_text,
                    "token_count": token_count,
                    "embedding_model": "text-embedding-3-small",
                }

                await self.chunk_repo.create({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "content": chunk_text,
                    "page_number": metadata["page_number"],
                    "source": doc["filename"],
                    "token_count": token_count,
                    "embedding_model": "text-embedding-3-small",
                })

                vectors.append((chunk_id, embedding, metadata))

            if vectors:
                await self.vector_store.upsert(self.workspace_id, vectors)

            return await self.doc_repo.update(document_id, {
                "status": DocumentStatus.INDEXED.value,
                "token_count": total_tokens,
                "page_count": page_count,
                "chunk_count": len(chunks),
            })
        except Exception as e:
            await self.doc_repo.update(document_id, {
                "status": DocumentStatus.FAILED.value,
                "error": str(e),
            })
            raise

    async def list_documents(self, skip: int = 0, limit: int = 50) -> tuple[list, int]:
        return await self.doc_repo.list(skip=skip, limit=limit, sort=[("created_at", -1)])

    async def delete_document(self, document_id: str) -> bool:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        await self.storage.delete_file(doc["s3_key"])
        await self.vector_store.delete_by_document(self.workspace_id, document_id)
        await self.chunk_repo.delete_by_document(document_id)
        return await self.doc_repo.delete(document_id)

    async def get_stats(self) -> dict:
        docs, total = await self.doc_repo.list(limit=1000)
        tokens = sum(d.get("token_count", 0) for d in docs)
        pages = sum(d.get("page_count", 0) for d in docs)
        indexed = sum(1 for d in docs if d.get("status") == DocumentStatus.INDEXED.value)
        last_sync = max((d.get("updated_at", "") for d in docs), default=None)

        return {
            "total_documents": total,
            "pages_indexed": pages,
            "tokens_indexed": tokens,
            "indexed_documents": indexed,
            "last_sync_time": str(last_sync) if last_sync else None,
            "coverage_score": round(indexed / max(total, 1) * 100, 1),
        }

    async def ingest_text(self, title: str, content: str, source: str = "crawler") -> dict:
        s3_key = await self.storage.upload_file(
            self.workspace_id, f"{title}.txt", content.encode()
        )
        doc = await self.doc_repo.create({
            "filename": title,
            "file_type": ".txt",
            "s3_key": s3_key,
            "status": DocumentStatus.PENDING.value,
            "source": source,
        })
        await self.process_document(doc["id"])
        return doc
