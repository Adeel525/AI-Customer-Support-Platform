# RAG Pipeline

## Overview

Retrieval-Augmented Generation pipeline for context-aware customer support responses.

## Document Ingestion

```
Upload → S3 Storage → Extract Text → Clean → Chunk → Embed → Pinecone + MongoDB
```

### Supported Formats
PDF, DOCX, TXT, MD, CSV, HTML

### Chunking Strategy
- **Size:** 800 tokens (configurable)
- **Overlap:** 150 tokens
- **Splitter:** LangChain RecursiveCharacterTextSplitter

### Embedding
- **Primary:** OpenAI text-embedding-3-small (1536 dimensions)
- **Fallback:** Deterministic hash-based vectors (dev mode)

## Query Flow

```
User Question
    ↓
Query Rewriting (with conversation history)
    ↓
Generate Query Embedding
    ↓
Pinecone Vector Search (top 20)
    +
MongoDB Keyword Search (top 5)
    ↓
Rerank & Deduplicate (top 5)
    ↓
Build Context Window
    ↓
LLM Generation (GPT-4o / Claude / fallback)
    ↓
Confidence Scoring
    ↓
Response + Source Citations
```

## Features

### Hybrid Search
Combines vector similarity (Pinecone) with keyword matching (MongoDB regex) for better recall.

### Query Rewriting
Follow-up questions are rewritten using conversation history for better retrieval.

### Confidence Scoring
- Embedding similarity scores from retrieval
- LLM self-assessment of answer accuracy
- Threshold: 0.6 (configurable via `CONFIDENCE_THRESHOLD`)

### Auto-Escalation
When confidence < 0.6, automatically:
1. Updates conversation status to "escalated"
2. Creates support ticket with AI-generated summary
3. Notifies customer about human agent connection

### Caching
Redis cache for repeated queries (TTL: 1 hour).

### Source Attribution
Each response includes citations with:
- Document ID and filename
- Page number
- Relevance score
- Content excerpt

## LLM Abstraction

Supports multiple providers with automatic fallback:
1. OpenAI GPT-4o (primary)
2. Anthropic Claude (secondary)
3. Demo mode message (no API key)

## Pinecone Configuration

- Index: `support-kb`
- Dimension: 1536
- Metric: cosine
- Namespace: `workspace_{workspace_id}` (tenant isolation)
- In-memory fallback when Pinecone unavailable
