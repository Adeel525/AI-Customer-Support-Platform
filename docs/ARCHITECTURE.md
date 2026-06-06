# Architecture

## Overview

SupportAI is a multi-tenant SaaS platform built with a clean architecture pattern separating concerns across API, service, repository, and AI layers.

## System Architecture

```
Clients (Dashboard, Widget, API)
    ↓
Nginx Reverse Proxy
    ↓
FastAPI Backend
    ├── Tenant Middleware (workspace isolation)
    ├── Authentication (JWT + OAuth)
    ├── API Endpoints (21 modules)
    ├── Services (business logic)
    ├── Repositories (MongoDB CRUD)
    └── AI Layer (RAG, embeddings, LLM)
    ↓
Data Layer
    ├── MongoDB (transactional data)
    ├── Pinecone (vector embeddings)
    ├── Redis (cache + Celery broker)
    └── S3 (document storage)
```

## Multi-Tenant Isolation

Every data document includes `workspace_id`. Isolation enforced at:

1. **JWT/Header** — `X-Workspace-Id` or token claim
2. **Repository** — All queries filter by `workspace_id`
3. **Pinecone** — Namespace per workspace (`workspace_{id}`)

## Backend Layers

| Layer | Responsibility |
|-------|---------------|
| Endpoints | HTTP routing, validation, auth guards |
| Services | Business rules, orchestration |
| Repositories | MongoDB data access |
| Schemas | Pydantic request/response DTOs |
| AI | LLM, embeddings, RAG pipeline |
| Workers | Celery async tasks |

## Key Services

- **AuthService** — Signup, login, JWT, OAuth, password reset
- **KnowledgeService** — Document upload, extraction, chunking, embedding
- **RAGEngine** — Query → embed → search → rerank → LLM → response
- **ChatService** — Public chat API with conversation management
- **TicketService** — Auto-generation on low confidence
- **AnalyticsService** — Metrics aggregation

## Background Jobs (Celery)

- `process_document` — Document ingestion pipeline
- `crawl_website` — Website crawler
- `aggregate_daily_analytics` — Nightly metrics (Beat)
- `sync_scheduled_crawlers` — Scheduled crawl sync (Beat)
- `summarize_conversation` — Post-session summarization

## Frontend Architecture

- **Next.js 15** App Router with route groups
- **Zustand** for auth state persistence
- **React Query** for server state
- **Shadcn UI** component library
- **Recharts** for analytics visualization

## Security

- JWT access (30 min) + refresh (7 days) tokens
- RBAC with 4 roles: owner, admin, agent, viewer
- Rate limiting on public endpoints
- Audit logging middleware
- S3 presigned URLs for uploads
