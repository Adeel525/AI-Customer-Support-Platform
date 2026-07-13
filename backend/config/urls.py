"""
URL configuration for SupportAI.

API routes live under /api/v1/ for frontend compatibility.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings


def health_check(_request):
    return JsonResponse(
        {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "1.0.0",
        }
    )


def root(_request):
    return JsonResponse(
        {
            "message": f"Welcome to {settings.APP_NAME} API",
            "docs": "/api/v1/",
            "health": "/health",
        }
    )


urlpatterns = [
    path("", root, name="root"),
    path("health", health_check, name="health"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
]
