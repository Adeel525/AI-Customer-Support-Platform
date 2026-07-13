# AI Customer Support SaaS Platform

Multi-tenant SaaS for AI-powered customer support chatbots trained on company documents, websites, and FAQs.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Backend | **Django 5.1 + Django REST Framework** |
| Database | MongoDB (mongoengine) |
| Vector DB | Pinecone |
| Cache / Jobs | Redis + Celery |
| Storage | AWS S3 / local |
| AI | OpenAI GPT-4o, Claude, LangChain |

## Quick Start

### Prerequisites

- Python 3.12+, Node.js 20+, MongoDB

### Backend (Django)

```bash
cp .env.example .env
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

### Frontend

```bash
cd frontend
npm install
set NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
npm run dev
```

### Access

- Dashboard: http://localhost:3000 (or 3002)
- API: http://localhost:8001/api/v1/
- Health: http://localhost:8001/health
- Admin: http://localhost:8001/admin/

### Celery (optional)

```bash
cd backend
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

### Docker

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

## Project Structure

```
├── backend/                 # Django + DRF
│   ├── config/              # settings, urls, wsgi, celery
│   ├── api/                 # models, views, serializers, auth
│   ├── core/                # AI/RAG, utils, enums
│   └── manage.py
├── frontend/                # Next.js dashboard
├── widget/                  # Embeddable chat widget
├── infrastructure/          # Docker, Nginx, monitoring
└── docs/
```

## API Compatibility

Frontend routes under `/api/v1/` are unchanged after the FastAPI → Django migration
(auth, workspaces, knowledge, chatbots, public chat, tickets, analytics, etc.).

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Reference](docs/API.md)
- [RAG Pipeline](docs/RAG_PIPELINE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Interview prep](learning.txt)

## License

Proprietary — All rights reserved.
