"""
DRF serializers for API requests (mongoengine — plain Serializer, not ModelSerializer).
"""
from __future__ import annotations

from rest_framework import serializers

from core.enums import (
    CrawlerSchedule,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    UserRole,
)


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    full_name = serializers.CharField(required=True, min_length=1, max_length=255)
    workspace_name = serializers.CharField(required=True, min_length=1, max_length=255)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)


class WorkspaceUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, min_length=1, max_length=255)
    support_email = serializers.EmailField(required=False, allow_null=True)
    business_hours = serializers.DictField(required=False, allow_null=True)
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
    )
    language = serializers.CharField(required=False, allow_null=True, max_length=32)
    custom_domain = serializers.CharField(required=False, allow_null=True, max_length=255)


class BrandingUpdateSerializer(serializers.Serializer):
    logo_url = serializers.URLField(required=False, allow_null=True)
    primary_color = serializers.CharField(required=False, allow_null=True, max_length=32)
    company_name = serializers.CharField(required=False, allow_null=True, max_length=255)


class MemberInviteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(
        choices=[r.value for r in UserRole if r != UserRole.OWNER],
        default=UserRole.AGENT.value,
    )


class ChatbotCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, min_length=1, max_length=255)
    welcome_message = serializers.CharField(
        required=False,
        default="Hi! How can I help you today?",
    )
    primary_color = serializers.CharField(required=False, default="#10b981", max_length=32)
    theme = serializers.CharField(required=False, default="light", max_length=32)
    language = serializers.CharField(required=False, default="en", max_length=16)
    tone = serializers.CharField(required=False, default="professional", max_length=64)
    personality = serializers.CharField(required=False, default="support", max_length=64)
    avatar_url = serializers.URLField(required=False, allow_null=True)
    document_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )


class ChatbotUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, min_length=1, max_length=255)
    welcome_message = serializers.CharField(required=False, allow_null=True)
    primary_color = serializers.CharField(required=False, allow_null=True, max_length=32)
    theme = serializers.CharField(required=False, allow_null=True, max_length=32)
    language = serializers.CharField(required=False, allow_null=True, max_length=16)
    tone = serializers.CharField(required=False, allow_null=True, max_length=64)
    personality = serializers.CharField(required=False, allow_null=True, max_length=64)
    avatar_url = serializers.URLField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    document_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
    )


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, min_length=1)
    conversation_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    customer_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class TicketCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, min_length=1, max_length=500)
    description = serializers.CharField(required=True, allow_blank=True)
    category = serializers.ChoiceField(
        choices=[c.value for c in TicketCategory],
        default=TicketCategory.TECHNICAL.value,
        required=False,
    )
    priority = serializers.ChoiceField(
        choices=[p.value for p in TicketPriority],
        default=TicketPriority.MEDIUM.value,
        required=False,
    )
    conversation_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class TicketUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, min_length=1, max_length=500)
    status = serializers.ChoiceField(
        choices=[s.value for s in TicketStatus],
        required=False,
    )
    priority = serializers.ChoiceField(
        choices=[p.value for p in TicketPriority],
        required=False,
    )
    assigned_agent_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    category = serializers.ChoiceField(
        choices=[c.value for c in TicketCategory],
        required=False,
    )


class TicketCommentSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, min_length=1)
    is_internal = serializers.BooleanField(required=False, default=False)


class FeedbackSerializer(serializers.Serializer):
    message_id = serializers.CharField(required=True)
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5, allow_null=True)
    comment = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    thumbs = serializers.ChoiceField(
        choices=["up", "down"],
        required=False,
        allow_null=True,
    )


class CrawlerJobCreateSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    schedule = serializers.ChoiceField(
        choices=[s.value for s in CrawlerSchedule],
        default=CrawlerSchedule.WEEKLY.value,
        required=False,
    )
    max_depth = serializers.IntegerField(required=False, default=2, min_value=1, max_value=10)
