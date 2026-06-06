# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Domain name (production)
- API keys: OpenAI, Pinecone (optional: Anthropic, Stripe, Google OAuth)

## Quick Start (Development)

```bash
cp .env.example .env
# Edit .env with your API keys

docker compose -f infrastructure/docker-compose.yml up -d
```

Access:
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)

## Production Deployment

### 1. Environment Variables

Set all variables in `.env`:
- `SECRET_KEY` — Generate a strong random key
- `MONGODB_URL` — Production MongoDB connection string
- `OPENAI_API_KEY` — Required for AI features
- `PINECONE_API_KEY` — Required for vector search
- `AWS_*` — S3 credentials for document storage
- `STRIPE_*` — Billing integration
- `GOOGLE_*` — OAuth credentials

### 2. Build and Deploy

```bash
docker compose -f infrastructure/docker-compose.yml build
docker compose -f infrastructure/docker-compose.yml up -d
```

### 3. SSL/TLS

Add SSL termination to Nginx or use a cloud load balancer.

### 4. Database

- Use MongoDB Atlas for managed MongoDB
- Enable automated backups
- Create indexes (done automatically on startup)

### 5. Monitoring

- Prometheus scrapes `/metrics` endpoint
- Grafana dashboards at port 3001
- Health check: `GET /health`

### 6. Scaling

- Scale `celery-worker` for document processing
- Scale `backend` behind load balancer
- Use Redis Cluster for high availability
- Pinecone serverless for vector storage

### 7. Backup Strategy

- MongoDB: Daily automated backups
- S3: Versioning enabled on document bucket
- Pinecone: Metadata stored in MongoDB as fallback

## CI/CD

GitHub Actions pipeline:
1. Backend tests (pytest + ruff)
2. Frontend build
3. Widget build
4. Docker build (main branch)
5. E2E tests (Playwright)
