"""
API v1 URL routes — mirrors FastAPI /api/v1 paths for frontend compatibility.
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.views.admin_assistant import AdminAssistantQueryView
from api.views.analytics import AnalyticsCsatView, AnalyticsHistoricalView, AnalyticsOverviewView
from api.views.api_keys import ApiKeyListCreateView, ApiKeyRevokeView
from api.views.auth import (
    ForgotPasswordView,
    GoogleCallbackView,
    GoogleLoginView,
    LoginView,
    MeView,
    RefreshView,
    ResetPasswordView,
    SignupView,
    VerifyEmailView,
)
from api.views.billing import BillingWebhookView, CheckoutView, SubscriptionView
from api.views.chat import (
    ConversationAssignView,
    ConversationDetailView,
    ConversationListView,
    PublicChatbotConfigView,
    PublicChatMessageView,
    PublicEscalateView,
    PublicFeedbackView,
)
from api.views.chatbots import ChatbotDetailView, ChatbotListCreateView
from api.views.crawler import CrawlerJobListCreateView, CrawlerJobSyncView
from api.views.integrations import (
    IntegrationConnectView,
    IntegrationDisconnectView,
    IntegrationListView,
    SlackWebhookView,
    WhatsAppWebhookView,
)
from api.views.knowledge import (
    DocumentDeleteView,
    DocumentListView,
    DocumentUploadView,
    KnowledgeStatsView,
)
from api.views.search import SearchView
from api.views.tickets import TicketCommentsView, TicketDetailView, TicketListCreateView
from api.views.voice import SpeechToTextView, TextToSpeechView
from api.views.workspaces import (
    BrandingView,
    CurrentWorkspaceView,
    MemberDetailView,
    MembersListView,
)


@api_view(["GET"])
def api_root(_request):
    return Response(
        {
            "message": "SupportAI API v1",
            "endpoints": [
                "auth/",
                "workspaces/",
                "knowledge/",
                "crawler/",
                "chatbots/",
                "chat/",
                "public/chat/",
                "tickets/",
                "analytics/",
                "search/",
                "integrations/",
                "billing/",
                "api-keys/",
                "admin-assistant/",
                "voice/",
            ],
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    # Auth
    path("auth/signup", SignupView.as_view(), name="auth-signup"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/refresh", RefreshView.as_view(), name="auth-refresh"),
    path("auth/me", MeView.as_view(), name="auth-me"),
    path("auth/verify-email", VerifyEmailView.as_view(), name="auth-verify-email"),
    path("auth/forgot-password", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("auth/reset-password", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("auth/google/login", GoogleLoginView.as_view(), name="auth-google-login"),
    path("auth/google/callback", GoogleCallbackView.as_view(), name="auth-google-callback"),
    # Workspaces
    path("workspaces/current", CurrentWorkspaceView.as_view(), name="workspaces-current"),
    path("workspaces/current/branding", BrandingView.as_view(), name="workspaces-branding"),
    path("workspaces/current/members", MembersListView.as_view(), name="workspaces-members"),
    path(
        "workspaces/current/members/<str:user_id>",
        MemberDetailView.as_view(),
        name="workspaces-member-detail",
    ),
    # Knowledge
    path("knowledge/documents/upload", DocumentUploadView.as_view(), name="knowledge-upload"),
    path("knowledge/documents", DocumentListView.as_view(), name="knowledge-documents"),
    path(
        "knowledge/documents/<str:document_id>",
        DocumentDeleteView.as_view(),
        name="knowledge-document-delete",
    ),
    path("knowledge/stats", KnowledgeStatsView.as_view(), name="knowledge-stats"),
    # Crawler
    path("crawler/jobs", CrawlerJobListCreateView.as_view(), name="crawler-jobs"),
    path("crawler/jobs/<str:job_id>/sync", CrawlerJobSyncView.as_view(), name="crawler-sync"),
    # Chatbots
    path("chatbots", ChatbotListCreateView.as_view(), name="chatbots"),
    path("chatbots/<str:chatbot_id>", ChatbotDetailView.as_view(), name="chatbot-detail"),
    # Public chat
    path(
        "public/chat/<str:chatbot_id>/config",
        PublicChatbotConfigView.as_view(),
        name="public-chat-config",
    ),
    path(
        "public/chat/<str:chatbot_id>/message",
        PublicChatMessageView.as_view(),
        name="public-chat-message",
    ),
    path(
        "public/chat/<str:chatbot_id>/escalate",
        PublicEscalateView.as_view(),
        name="public-chat-escalate",
    ),
    path("public/chat/feedback", PublicFeedbackView.as_view(), name="public-chat-feedback"),
    # Authenticated chat
    path("chat/conversations", ConversationListView.as_view(), name="chat-conversations"),
    path(
        "chat/conversations/<str:conversation_id>",
        ConversationDetailView.as_view(),
        name="chat-conversation-detail",
    ),
    path(
        "chat/conversations/<str:conversation_id>/assign",
        ConversationAssignView.as_view(),
        name="chat-conversation-assign",
    ),
    # Tickets
    path("tickets", TicketListCreateView.as_view(), name="tickets"),
    path("tickets/<str:ticket_id>", TicketDetailView.as_view(), name="ticket-detail"),
    path(
        "tickets/<str:ticket_id>/comments",
        TicketCommentsView.as_view(),
        name="ticket-comments",
    ),
    # Analytics
    path("analytics/overview", AnalyticsOverviewView.as_view(), name="analytics-overview"),
    path("analytics/historical", AnalyticsHistoricalView.as_view(), name="analytics-historical"),
    path("analytics/csat", AnalyticsCsatView.as_view(), name="analytics-csat"),
    # Search
    path("search", SearchView.as_view(), name="search"),
    # Integrations (webhooks before parameterized routes)
    path("integrations", IntegrationListView.as_view(), name="integrations"),
    path(
        "integrations/webhooks/whatsapp",
        WhatsAppWebhookView.as_view(),
        name="integrations-whatsapp-webhook",
    ),
    path(
        "integrations/webhooks/slack",
        SlackWebhookView.as_view(),
        name="integrations-slack-webhook",
    ),
    path(
        "integrations/<str:integration_type>/connect",
        IntegrationConnectView.as_view(),
        name="integrations-connect",
    ),
    path(
        "integrations/<str:integration_id>",
        IntegrationDisconnectView.as_view(),
        name="integrations-disconnect",
    ),
    # Billing
    path("billing/subscription", SubscriptionView.as_view(), name="billing-subscription"),
    path("billing/checkout", CheckoutView.as_view(), name="billing-checkout"),
    path("billing/webhook", BillingWebhookView.as_view(), name="billing-webhook"),
    # API keys
    path("api-keys", ApiKeyListCreateView.as_view(), name="api-keys"),
    path("api-keys/<str:key_id>", ApiKeyRevokeView.as_view(), name="api-keys-revoke"),
    # Admin assistant
    path("admin-assistant/query", AdminAssistantQueryView.as_view(), name="admin-assistant-query"),
    # Voice
    path("voice/stt", SpeechToTextView.as_view(), name="voice-stt"),
    path("voice/tts", TextToSpeechView.as_view(), name="voice-tts"),
]
