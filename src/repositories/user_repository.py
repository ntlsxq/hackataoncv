from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src import models


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[models.User]:
        query = select(models.User).where(models.User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[models.User]:
        query = select(models.User).where(models.User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, email: str, password: str | None) -> models.User:
        user = models.User(email=email, password=password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()