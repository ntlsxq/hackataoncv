from fastapi import Depends, HTTPException, Request
from starlette import status

from src.dependencies.misc import get_user_service
from src.schemas import User
from src.services.user_service import UserService
from src.utils.jwt import decode_access_token


async def get_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service),
) -> User:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )

    token = auth_header[len("Bearer "):].strip()

    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )

    user = await user_service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )

    return user