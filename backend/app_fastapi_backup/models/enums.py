from enum import Enum


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    AGENT = "agent"
    VIEWER = "viewer"


class Permission(str, Enum):
    MANAGE_WORKSPACE = "manage_workspace"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_KNOWLEDGE = "manage_knowledge"
    MANAGE_CHATBOTS = "manage_chatbots"
    MANAGE_TICKETS = "manage_tickets"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_BILLING = "manage_billing"
    MANAGE_INTEGRATIONS = "manage_integrations"
    LIVE_CHAT = "live_chat"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.OWNER: set(Permission),
    UserRole.ADMIN: {
        Permission.MANAGE_WORKSPACE,
        Permission.MANAGE_MEMBERS,
        Permission.MANAGE_KNOWLEDGE,
        Permission.MANAGE_CHATBOTS,
        Permission.MANAGE_TICKETS,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_INTEGRATIONS,
        Permission.LIVE_CHAT,
    },
    UserRole.AGENT: {
        Permission.MANAGE_TICKETS,
        Permission.VIEW_ANALYTICS,
        Permission.LIVE_CHAT,
    },
    UserRole.VIEWER: {
        Permission.VIEW_ANALYTICS,
    },
}


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    AGENT = "agent"
    SYSTEM = "system"


class TicketCategory(str, Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    REFUND = "refund"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class IntegrationType(str, Enum):
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    EMAIL = "email"


class CrawlerSchedule(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CrawlerStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
