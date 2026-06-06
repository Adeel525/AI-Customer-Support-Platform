import hashlib
import logging
from typing import List

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = 1536

    async def embed_text(self, text: str) -> list[float]:
        if self.client:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        return self._fallback_embedding(text)

    async def embed_batch(self, texts: List[str]) -> list[list[float]]:
        if self.client:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> list[float]:
        """Deterministic hash-based fallback when OpenAI is unavailable."""
        h = hashlib.sha256(text.encode()).digest()
        vec = []
        for i in range(self.dimension):
            byte_val = h[i % len(h)]
            vec.append((byte_val / 255.0) * 2 - 1)
        return vec
