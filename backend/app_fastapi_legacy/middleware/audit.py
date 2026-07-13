import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import get_database


class AuditMiddleware(BaseHTTPMiddleware):
    AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        if request.method in self.AUDIT_METHODS and response.status_code < 400:
            try:
                tenant = getattr(request.state, "tenant", None)
                user_id = tenant.user_id if tenant else None
                workspace_id = tenant.workspace_id if tenant else None

                if user_id and workspace_id:
                    db = get_database()
                    await db.audit_logs.insert_one({
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "action": f"{request.method} {request.url.path}",
                        "resource": request.url.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2),
                        "timestamp": datetime.now(timezone.utc),
                    })
            except Exception:
                pass

        return response
