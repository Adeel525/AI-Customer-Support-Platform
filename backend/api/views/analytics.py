"""
Analytics API views — overview, historical, CSAT.
"""
from __future__ import annotations

from collections import Counter

from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import Analytics, Conversation, Feedback, Message, Ticket, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from core.enums import Permission


def _csat_stats(workspace_id: str) -> dict:
    feedbacks = list(Feedback.objects(workspace_id=workspace_id))
    if not feedbacks:
        return {"avg_rating": 0, "total": 0, "csat_score": 0}

    ratings = [f.rating for f in feedbacks if f.rating is not None]
    total = len(feedbacks)
    avg = sum(ratings) / max(len(ratings), 1) if ratings else 0
    positive = sum(1 for r in ratings if r >= 4)
    return {
        "avg_rating": round(avg, 2),
        "total": total,
        "csat_score": round(positive / max(len(ratings), 1) * 100, 1) if ratings else 0,
    }


def _overview(workspace_id: str) -> dict:
    convs = list(Conversation.objects(workspace_id=workspace_id))
    total_conv = len(convs)
    resolved = sum(1 for c in convs if c.status == "resolved")
    escalated = sum(1 for c in convs if c.status == "escalated")
    ticket_count = Ticket.objects(workspace_id=workspace_id).count()
    csat = _csat_stats(workspace_id)

    confidences = [c.last_confidence for c in convs if c.last_confidence is not None]
    avg_confidence = sum(confidences) / max(len(confidences), 1)

    user_msgs = Message.objects(workspace_id=workspace_id, role="user")
    counter = Counter((m.content or "")[:100] for m in user_msgs)
    top_questions = [{"question": q, "count": n} for q, n in counter.most_common(10) if q]

    records = list(
        Analytics.objects(workspace_id=workspace_id).order_by("date")
    )
    confidence_trend = [
        {
            "date": r.date,
            "accuracy": (r.metrics or {}).get("chatbot_accuracy", 0),
        }
        for r in records[-30:]
    ]

    return {
        "total_conversations": total_conv,
        "resolved_conversations": resolved,
        "escalated_conversations": escalated,
        "avg_response_time_ms": 0,
        "csat_score": csat.get("csat_score", 0),
        "ticket_volume": ticket_count,
        "chatbot_accuracy": round(avg_confidence * 100, 1),
        "top_questions": top_questions,
        "confidence_trend": confidence_trend,
    }


class AnalyticsOverviewView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.VIEW_ANALYTICS.value)]

    def get(self, request):
        return Response(_overview(get_workspace_id(request)))


class AnalyticsHistoricalView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.VIEW_ANALYTICS.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        start_date = request.query_params.get("start_date", "2020-01-01")
        end_date = request.query_params.get("end_date", "2099-12-31")

        records = Analytics.objects(
            workspace_id=ws_id,
            date__gte=start_date,
            date__lte=end_date,
        ).order_by("date")
        return Response([serialize_doc(r) for r in records])


class AnalyticsCsatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.VIEW_ANALYTICS.value)]

    def get(self, request):
        return Response(_csat_stats(get_workspace_id(request)))
