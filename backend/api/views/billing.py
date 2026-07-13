"""
Billing API views — subscription get; checkout/webhook stubs.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import Subscription, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from core.enums import Permission, SubscriptionPlan


class SubscriptionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_BILLING.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        sub = Subscription.objects(workspace_id=ws_id).first()
        if sub:
            return Response(serialize_doc(sub))
        return Response({
            "workspace_id": ws_id,
            "plan": SubscriptionPlan.FREE.value,
            "usage": {"documents": 0, "messages": 0, "users": 0},
        })


class CheckoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_BILLING.value)]

    def post(self, request):
        return Response(
            {"detail": "Stripe checkout not configured. Set STRIPE_SECRET_KEY."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class BillingWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {"detail": "Stripe webhook handler not configured."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
