import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.interview import InterviewChat, InterviewMessage, MessageRole


class InterviewChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chat(
        self,
        owner_id: uuid.UUID,
        title: str | None = None,
        position: str | None = None,
    ) -> InterviewChat:
        chat = InterviewChat(
            owner_id=owner_id,
            title=title,
            position=position,
        )
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def get_chat_by_id(
        self, chat_id: uuid.UUID, owner_id: uuid.UUID
    ) -> Optional[InterviewChat]:
        query = (
            select(InterviewChat)
            .where(InterviewChat.id == chat_id)
            .where(InterviewChat.owner_id == owner_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_chats_for_user(
        self, owner_id: uuid.UUID
    ) -> List[InterviewChat]:
        query = (
            select(InterviewChat)
            .where(InterviewChat.owner_id == owner_id)
            .order_by(InterviewChat.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_chat(self, chat: InterviewChat) -> None:
        await self.session.delete(chat)
        await self.session.commit()

    async def add_message(
        self,
        chat_id: uuid.UUID,
        role: MessageRole,
        content: str,
    ) -> InterviewMessage:
        msg = InterviewMessage(chat_id=chat_id, role=role, content=content)
        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        return msg

    async def get_messages_for_chat(
        self, chat_id: uuid.UUID
    ) -> List[InterviewMessage]:
        query = (
            select(InterviewMessage)
            .where(InterviewMessage.chat_id == chat_id)
            .order_by(InterviewMessage.created_at.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_title(
            self,
            chat: InterviewChat,
            title: str,
    ) -> InterviewChat:
        chat.title = title
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat