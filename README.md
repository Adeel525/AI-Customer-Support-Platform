# AI Customer Support SaaS Platform

Production-grade multi-tenant SaaS platform for AI-powered customer support chatbots trained on company documents, websites, FAQs, and knowledge bases.

## Features

- Multi-tenant workspace management with RBAC
- Knowledge base with document upload and website crawling
- RAG-powered AI chatbot with source citations
- Embeddable chat widget for any website
- Live chat with WebSocket support
- Automated support ticket generation
- Analytics dashboard with CSAT tracking
- API platform with rate limiting
- Subscription billing (Stripe)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, Shadcn UI |
| Backend | FastAPI, Python 3.12 |
| Database | MongoDB |
| Vector DB | Pinecone |
| Cache | Redis |
| Jobs | Celery |
| Storage | AWS S3 |
| AI | OpenAI GPT-4o, Claude, LangChain |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Development

```bash
# Copy environment variables
cp .env.example .env

# Start all services
docker compose -f infrastructure/docker-compose.yml up -d

# Or run individually:

# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Widget
cd widget && npm install && npm run build
```

### Access

- Dashboard: http://localhost:3000
- API: http://localhost:8000/api/v1
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001

## Project Structure

```
├── backend/          # FastAPI application
├── frontend/         # Next.js dashboard
├── widget/           # Embeddable chat widget
├── infrastructure/   # Docker, Nginx, monitoring
└── docs/             # Architecture & API documentation
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Reference](docs/API.md)
- [RAG Pipeline](docs/RAG_PIPELINE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

Proprietary — All rights reserved.
