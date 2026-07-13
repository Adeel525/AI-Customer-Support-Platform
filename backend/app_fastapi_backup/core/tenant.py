from dataclasses import dataclass

from fastapi import Request


@dataclass
class TenantContext:
    workspace_id: str
    user_id: str
    role: str


def get_tenant_from_request(request: Request) -> TenantContext | None:
    return getattr(request.state, "tenant", None)
