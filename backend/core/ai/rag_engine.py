import hashlib
import json
import logging
from typing import Generator

import redis

from core.ai.embeddings import EmbeddingService
from core.ai.llm_client import LLMClient
from core.ai.prompts.support import CONFIDENCE_PROMPT, QUERY_REWRITE_PROMPT, SUPPORT_SYSTEM_PROMPT
from core.ai.vector_store import VectorStore
from core.config import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    def __init__(self, workspace_id: str, chunk_repo=None):
        """
        Sync RAG engine for Django views.

        Args:
            workspace_id: Tenant workspace id.
            chunk_repo: Optional object with keyword_search(query, limit) -> list[dict].
                        Inject a Django/mongoengine repository when available.
        """
        self.workspace_id = workspace_id
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStore()
        self.llm = LLMClient()
        self.chunk_repo = chunk_repo
        self._redis: redis.Redis | None = None

    def _get_redis(self) -> redis.Redis | None:
        if self._redis is None:
            try:
                self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                pass
        return self._redis

    def query(
        self,
        question: str,
        chatbot_config: dict | None = None,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        cache_key = self._cache_key(question)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        search_query = self._rewrite_query(question, conversation_history or [])
        query_vector = self.embeddings.embed_text(search_query)

        vector_results = self.vector_store.search(
            self.workspace_id,
            query_vector,
            top_k=settings.RAG_TOP_K,
        )

        if self.chunk_repo is not None:
            keyword_results = self.chunk_repo.keyword_search(search_query, limit=5)
            for kr in keyword_results:
                vector_results.append({
                    "id": kr.get("chunk_id", kr["id"]),
                    "score": 0.5,
                    "metadata": {
                        "content": kr.get("content", ""),
                        "document_id": kr.get("document_id", ""),
                        "source": kr.get("source", ""),
                        "page_number": kr.get("page_number", 0),
                    },
                })

        reranked = self._rerank(vector_results)[: settings.RAG_RERANK_TOP_K]
        context = self._build_context(reranked)
        sources = self._extract_sources(reranked)

        config = chatbot_config or {}
        system_prompt = SUPPORT_SYSTEM_PROMPT.format(
            company_name=config.get("name", "our company"),
            tone=config.get("tone", "professional"),
            personality=config.get("personality", "support"),
            context=context or "No relevant context found.",
        )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": question})

        answer = self.llm.generate(messages)
        confidence = self._calculate_confidence(question, answer, bool(context))
        avg_score = sum(r.get("score", 0) for r in reranked) / max(len(reranked), 1)
        confidence = max(confidence, min(avg_score, 1.0))

        result = {
            "content": answer,
            "confidence": round(confidence, 3),
            "sources": sources,
            "should_escalate": confidence < settings.CONFIDENCE_THRESHOLD,
        }

        self._set_cached(cache_key, result)
        return result

    def query_stream(
        self,
        question: str,
        chatbot_config: dict | None = None,
        conversation_history: list[dict] | None = None,
    ) -> Generator[str, None, None]:
        search_query = self._rewrite_query(question, conversation_history or [])
        query_vector = self.embeddings.embed_text(search_query)
        vector_results = self.vector_store.search(
            self.workspace_id, query_vector, top_k=settings.RAG_TOP_K
        )
        reranked = self._rerank(vector_results)[: settings.RAG_RERANK_TOP_K]
        context = self._build_context(reranked)

        config = chatbot_config or {}
        system_prompt = SUPPORT_SYSTEM_PROMPT.format(
            company_name=config.get("name", "our company"),
            tone=config.get("tone", "professional"),
            personality=config.get("personality", "support"),
            context=context or "No relevant context found.",
        )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": question})

        yield from self.llm.generate_stream(messages)

    def _rewrite_query(self, question: str, history: list[dict]) -> str:
        if not history:
            return question
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history[-4:])
        prompt = QUERY_REWRITE_PROMPT.format(history=history_text, question=question)
        rewritten = self.llm.generate(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )
        return rewritten.strip() or question

    def _rerank(self, results: list[dict]) -> list[dict]:
        seen = set()
        unique = []
        for r in sorted(results, key=lambda x: x.get("score", 0), reverse=True):
            content = r.get("metadata", {}).get("content", "")[:100]
            if content not in seen:
                seen.add(content)
                unique.append(r)
        return unique

    def _build_context(self, results: list[dict]) -> str:
        parts = []
        for i, r in enumerate(results, 1):
            meta = r.get("metadata", {})
            content = meta.get("content", "")
            source = meta.get("source", "unknown")
            page = meta.get("page_number", "")
            parts.append(f"[Source {i}: {source}, page {page}]\n{content}")
        return "\n\n---\n\n".join(parts)

    def _extract_sources(self, results: list[dict]) -> list[dict]:
        sources = []
        for r in results:
            meta = r.get("metadata", {})
            sources.append({
                "document_id": meta.get("document_id", ""),
                "source": meta.get("source", ""),
                "page_number": meta.get("page_number", 0),
                "score": round(r.get("score", 0), 3),
                "excerpt": meta.get("content", "")[:200],
            })
        return sources

    def _calculate_confidence(self, question: str, answer: str, has_context: bool) -> float:
        if not has_context:
            return 0.2
        prompt = CONFIDENCE_PROMPT.format(
            question=question, answer=answer, has_context=has_context
        )
        try:
            result = self.llm.generate(
                [{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10,
            )
            return float(result.strip())
        except (ValueError, TypeError):
            return 0.5

    def _cache_key(self, question: str) -> str:
        h = hashlib.md5(f"{self.workspace_id}:{question}".encode()).hexdigest()
        return f"rag:{h}"

    def _get_cached(self, key: str) -> dict | None:
        client = self._get_redis()
        if not client:
            return None
        try:
            data = client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def _set_cached(self, key: str, data: dict) -> None:
        client = self._get_redis()
        if not client:
            return
        try:
            client.setex(key, 3600, json.dumps(data))
        except Exception:
            pass
