# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Create account + workspace |
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/verify-email` | Verify email address |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |
| GET | `/auth/me` | Get current user + workspaces |
| GET | `/auth/google/login` | Initiate Google OAuth |
| GET | `/auth/google/callback` | OAuth callback |

## Workspaces

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workspaces/current` | Get current workspace |
| PATCH | `/workspaces/current` | Update workspace settings |
| PATCH | `/workspaces/current/branding` | Update branding |
| GET | `/workspaces/current/members` | List members |
| POST | `/workspaces/current/members` | Invite member |
| PATCH | `/workspaces/current/members/{id}` | Update member role |
| DELETE | `/workspaces/current/members/{id}` | Remove member |

## Knowledge Base

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/knowledge/documents/upload` | Upload document (multipart) |
| GET | `/knowledge/documents` | List documents |
| DELETE | `/knowledge/documents/{id}` | Delete document |
| GET | `/knowledge/stats` | Knowledge base statistics |

## Chatbots

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chatbots` | Create chatbot |
| GET | `/chatbots` | List chatbots |
| GET | `/chatbots/{id}` | Get chatbot |
| PATCH | `/chatbots/{id}` | Update chatbot |
| DELETE | `/chatbots/{id}` | Delete chatbot |

## Public Chat (no auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/public/chat/{id}/config` | Get chatbot config |
| POST | `/public/chat/{id}/message` | Send message |
| POST | `/public/chat/{id}/escalate` | Escalate to human |
| POST | `/public/chat/feedback` | Submit feedback |

## Tickets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tickets` | Create ticket |
| GET | `/tickets` | List tickets |
| GET | `/tickets/{id}` | Get ticket |
| PATCH | `/tickets/{id}` | Update ticket |
| POST | `/tickets/{id}/comments` | Add comment |
| GET | `/tickets/{id}/comments` | List comments |

## Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/overview` | Dashboard metrics |
| GET | `/analytics/historical` | Historical data |
| GET | `/analytics/csat` | CSAT score |

## Headers

```
Authorization: Bearer <access_token>
X-Workspace-Id: <workspace_id>
```
