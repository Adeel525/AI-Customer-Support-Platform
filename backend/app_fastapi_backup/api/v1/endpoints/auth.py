from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from starlette.config import Config

from app.core.config import settings
from app.core.database import get_database
from app.core.deps import CurrentUser
from app.schemas.auth import (
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserResponse,
    UserSignup,
    VerifyEmailRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service():
    return AuthService(get_database())


@router.post("/signup", response_model=dict)
async def signup(data: UserSignup, service: AuthService = Depends(get_auth_service)):
    return await service.signup(data.email, data.password, data.full_name, data.workspace_name)


@router.post("/login", response_model=dict)
async def login(data: UserLogin, service: AuthService = Depends(get_auth_service)):
    return await service.login(data.email, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)):
    return await service.refresh_token(data.refresh_token)


@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest, service: AuthService = Depends(get_auth_service)):
    await service.verify_email(data.token)
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)):
    await service.forgot_password(data.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)):
    await service.reset_password(data.token, data.new_password)
    return {"message": "Password reset successfully"}


@router.get("/me")
async def get_me(user: CurrentUser, service: AuthService = Depends(get_auth_service)):
    return await service.get_me(user["id"])


@router.get("/google/login")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID:
        return {"error": "Google OAuth not configured"}
    from authlib.integrations.starlette_client import OAuth
    config = Config(environ={
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
    })
    oauth = OAuth(config)
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, service: AuthService = Depends(get_auth_service)):
    from authlib.integrations.starlette_client import OAuth
    from starlette.config import Config as StarletteConfig
    config = StarletteConfig(environ={
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
    })
    oauth = OAuth(config)
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo", {})
    result = await service.handle_oauth_user(
        user_info.get("email", ""),
        user_info.get("name", ""),
        "google",
    )
    return RedirectResponse(
        f"{settings.FRONTEND_URL}/auth/callback?access_token={result['access_token']}&refresh_token={result['refresh_token']}"
    )
