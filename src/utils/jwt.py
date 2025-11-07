import uuid

import jwt
from datetime import datetime, timedelta
from typing import Optional

from src.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 час


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[uuid.UUID]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return uuid.UUID(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None