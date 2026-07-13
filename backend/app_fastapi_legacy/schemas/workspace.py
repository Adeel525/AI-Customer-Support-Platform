from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str | None = None


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    support_email: str | None = None
    business_hours: dict | None = None
    categories: list[str] | None = None
    language: str | None = None
    custom_domain: str | None = None


class BrandingUpdate(BaseModel):
    logo_url: str | None = None
    primary_color: str | None = None
    company_name: str | None = None


class MemberInvite(BaseModel):
    email: str
    role: str = "agent"


class MemberRoleUpdate(BaseModel):
    role: str


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: str
    branding: dict = {}
    settings: dict = {}
    plan: str = "free"
