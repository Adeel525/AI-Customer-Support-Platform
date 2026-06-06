# Database Schema

## MongoDB Collections

### users
| Field | Type | Description |
|-------|------|-------------|
| email | string | Unique, lowercase |
| password_hash | string | bcrypt hash (null for OAuth) |
| full_name | string | Display name |
| is_verified | boolean | Email verification status |
| oauth_provider | string | google, null |
| verification_token | string | Email verification |
| reset_token | string | Password reset |
| created_at | datetime | |
| updated_at | datetime | |

**Index:** `email` (unique)

### workspaces
| Field | Type | Description |
|-------|------|-------------|
| name | string | Workspace name |
| slug | string | URL-friendly identifier |
| branding | object | logo_url, primary_color, company_name |
| settings | object | support_email, business_hours, categories, language |
| plan | string | free, starter, professional, enterprise |

**Index:** `slug` (unique)

### workspace_members
| Field | Type | Description |
|-------|------|-------------|
| workspace_id | string | FK to workspaces |
| user_id | string | FK to users |
| role | string | owner, admin, agent, viewer |

**Index:** `(workspace_id, user_id)` (unique)

### documents
| Field | Type | Description |
|-------|------|-------------|
| workspace_id | string | Tenant isolation |
| filename | string | Original filename |
| file_type | string | .pdf, .docx, etc. |
| s3_key | string | Storage key |
| status | string | pending, processing, indexed, failed |
| token_count | int | Total tokens indexed |
| page_count | int | Number of pages |
| source | string | upload, crawler |

**Index:** `workspace_id`

### document_chunks
| Field | Type | Description |
|-------|------|-------------|
| workspace_id | string | Tenant isolation |
| document_id | string | Parent document |
| chunk_id | string | Unique chunk identifier |
| content | string | Chunk text |
| page_number | int | Source page |
| token_count | int | Tokens in chunk |

**Index:** `(workspace_id, document_id)`

### chatbots
| Field | Type | Description |
|-------|------|-------------|
| workspace_id | string | Tenant isolation |
| name | string | Chatbot name |
| welcome_message | string | Greeting text |
| primary_color | string | Hex color |
| theme | string | light, dark |
| tone | string | professional, friendly, etc. |
| personality | string | support, sales, technical |
| is_active | boolean | Public availability |

### conversations
| Field | Type | Description |
|-------|------|-------------|
| workspace_id | string | Tenant isolation |
| chatbot_id | string | Associated chatbot |
| customer_id | string | Anonymous customer ID |
| status | string | active, escalated, resolved, closed |
| assigned_agent_id | string | Human agent |
| summary | string | AI-generated summary |

### messages
| Field | Type | Description |
|-------|------|-------------|
| conversation_id | string | Parent conversation |
| workspace_id | string | Tenant isolation |
| role | string | user, assistant, agent, system |
| content | string | Message text |
| confidence | float | RAG confidence score |
| sources | array | Citation sources |

### tickets
| Field | Type | Description |
|-------|------|-------------|
| workspace_id | string | Tenant isolation |
| title | string | Ticket title |
| description | string | Issue description |
| category | string | technical, billing, refund, etc. |
| priority | string | low, medium, high, critical |
| status | string | open, pending, resolved, closed |
| conversation_id | string | Linked conversation |
| ai_summary | string | AI-generated summary |
| auto_generated | boolean | Created by AI escalation |

### analytics
| Field | Type | Description |
|-------|------|-------------|
| workspace_id | string | Tenant isolation |
| date | string | YYYY-MM-DD |
| metrics | object | Aggregated metrics snapshot |

**Index:** `(workspace_id, date)` (unique)

## Pinecone

- **Index:** `support-kb`
- **Dimension:** 1536
- **Metric:** cosine
- **Namespace:** `workspace_{workspace_id}` per tenant
