"""
Ticket API views — CRUD and comments.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import Ticket, TicketComment, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from api.serializers import TicketCommentSerializer, TicketCreateSerializer, TicketUpdateSerializer
from core.enums import Permission, TicketStatus


class TicketListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_TICKETS.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        status_filter = request.query_params.get("status")
        try:
            skip = int(request.query_params.get("skip", 0))
            limit = int(request.query_params.get("limit", 50))
        except (TypeError, ValueError):
            skip, limit = 0, 50
        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        qs = Ticket.objects(workspace_id=ws_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        qs = qs.order_by("-created_at")
        total = qs.count()
        items = [serialize_doc(t) for t in qs.skip(skip).limit(limit)]
        return Response({"items": items, "total": total})

    def post(self, request):
        ws_id = get_workspace_id(request)
        ser = TicketCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        ticket = Ticket(
            workspace_id=ws_id,
            title=data["title"],
            description=data.get("description", ""),
            category=data.get("category", "technical"),
            priority=data.get("priority", "medium"),
            status=TicketStatus.OPEN.value,
            conversation_id=data.get("conversation_id") or None,
            created_by=request.user.id,
        )
        ticket.save()
        return Response(serialize_doc(ticket), status=status.HTTP_201_CREATED)


class TicketDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_TICKETS.value)]

    def get(self, request, ticket_id):
        ws_id = get_workspace_id(request)
        ticket = Ticket.objects(id=ticket_id, workspace_id=ws_id).first()
        if not ticket:
            return Response({"detail": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_doc(ticket))

    def patch(self, request, ticket_id):
        ws_id = get_workspace_id(request)
        ticket = Ticket.objects(id=ticket_id, workspace_id=ws_id).first()
        if not ticket:
            return Response({"detail": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = TicketUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for key, value in ser.validated_data.items():
            if value is not None:
                setattr(ticket, key, value)
        ticket.save()
        return Response(serialize_doc(ticket))


class TicketCommentsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_TICKETS.value)]

    def get(self, request, ticket_id):
        ws_id = get_workspace_id(request)
        ticket = Ticket.objects(id=ticket_id, workspace_id=ws_id).first()
        if not ticket:
            return Response({"detail": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
        comments = [
            serialize_doc(c)
            for c in TicketComment.objects(ticket_id=ticket_id).order_by("created_at")
        ]
        return Response({"items": comments, "total": len(comments)})

    def post(self, request, ticket_id):
        ws_id = get_workspace_id(request)
        ticket = Ticket.objects(id=ticket_id, workspace_id=ws_id).first()
        if not ticket:
            return Response({"detail": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = TicketCommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        comment = TicketComment(
            ticket_id=ticket_id,
            workspace_id=ws_id,
            author_id=request.user.id,
            content=data["content"],
            is_internal=data.get("is_internal", False),
        )
        comment.save()
        return Response(serialize_doc(comment), status=status.HTTP_201_CREATED)
