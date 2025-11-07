import urllib

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette import status
from authlib.integrations.starlette_client import OAuth

from src.config import settings
from src.dependencies.auth import get_current_user
from src.dependencies.misc import get_user_service
from src.schemas.user_schemas import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginResponse,
    UserLoginRequest,
    User,
)
from src.services.user_service import UserService
from src.utils import jwt
from src import utils

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    user: UserRegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    try:
        created_user = await user_service.register_user(
            email=user.email,
            password=user.password
        )
        return UserRegisterResponse(
            user=created_user,
            token=jwt.create_access_token(created_user.id)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=UserLoginResponse)
async def login(
    user: UserLoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    authenticated_user = await user_service.authenticate_user(
        email=user.email,
        password=user.password
    )

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    return UserLoginResponse(
        user=user_service.user_model_to_schema(authenticated_user),
        token=jwt.create_access_token(authenticated_user.id)
    )

@router.get("/me", response_model=User)
async def me(user: User = Depends(get_current_user)):
    return user


@router.get("/google/login")
async def google_login():
    params = {
        "client_id": settings.GOOGLE_AUTH_CLIENT_ID,
        "redirect_uri": f"{settings.DOMAIN}/api/auth/google/callback/",
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_AUTH_CLIENT_ID,
        "client_secret": settings.GOOGLE_AUTH_SECRET,
        "redirect_uri": f"{settings.DOMAIN}/api/auth/google/callback/",
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        try:
            token_res = await client.post(token_url, data=data)
            token_res.raise_for_status()
            tokens = token_res.json()

            userinfo_res = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            userinfo_res.raise_for_status()
            user_info = userinfo_res.json()
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Something went wrong while authenticating with Google."
            )

    user = await user_service.register_or_login_google(
        email=user_info["email"],
    )

    token = jwt.create_access_token(user.id)

    return {"token": token, "user": user}