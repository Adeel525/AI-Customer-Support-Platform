"""
ASGI config for SupportAI.

It exposes the ASGI callable as a module-level variable named ``application``.
Supports HTTP and (optionally) WebSocket via Django Channels.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

try:
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter

    # WebSocket URL routes will be wired here once channels consumers exist.
    application = ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": AuthMiddlewareStack(URLRouter([])),
        }
    )
except ImportError:
    application = django_asgi_app
