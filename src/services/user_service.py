import uuid

import bcrypt
from typing import Optional

from pydantic import EmailStr

from src import schemas, models
from src.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @staticmethod
    def user_model_to_schema(user: models.User) -> schemas.User:
        return schemas.User(id=user.id,
                            email=user.email)

    async def get(self, user_id: uuid.UUID) -> Optional[schemas.User]:
        user = await self.user_repository.get_by_id(user_id)
        return user

    async def register_user(self, email: str, password: str) -> schemas.User:
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists.")

        hashed_password = self._hash_password(password)
        user = await self.user_repository.create(email=email, password=hashed_password)
        return self.user_model_to_schema(user)

    async def authenticate_user(self, email: str, password: str) -> Optional[models.User]:
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None

        if not self._verify_password(password, user.password):
            return None

        return user

    async def register_or_login(self, email: str, password: Optional[str] = None) -> schemas.User:
        user = await self.user_repository.get_by_email(email)
        if user:
            return self.user_model_to_schema(user)

        if not password:
            raise ValueError("Password required for new registration.")

        hashed_password = self._hash_password(password)
        new_user = await self.user_repository.create(email=email, password=hashed_password)
        return self.user_model_to_schema(new_user)

    async def register_or_login_google(self, email: str) -> schemas.User:
        user = await self.user_repository.get_by_email(email)
        if user:
            return self.user_model_to_schema(user)

        new_user = await self.user_repository.create(
            email=email,
            password=None
        )
        return self.user_model_to_schema(new_user)

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )