import uuid
from typing import List

from src import schemas
from src.models.interview import MessageRole
from src.repositories.interview_repository import InterviewChatRepository
from src.utils.ai import generate_interview_reply, generate_chat_title


class InterviewChatService:
    def __init__(self, repo: InterviewChatRepository):
        self.repo = repo

    async def create_chat(
        self,
        owner_id: uuid.UUID,
        title: str | None,
        position: str | None,
    ) -> schemas.InterviewChat:
        chat = await self.repo.create_chat(owner_id, title, position)
        return schemas.InterviewChat.model_validate(chat)

    async def get_chat_detail(
        self, chat_id: uuid.UUID, owner_id: uuid.UUID
    ) -> schemas.InterviewChatDetail:
        chat = await self.repo.get_chat_by_id(chat_id, owner_id)
        if not chat:
            return None  # роутер кинет 404

        messages = await self.repo.get_messages_for_chat(chat.id)
        return schemas.InterviewChatDetail(
            **schemas.InterviewChat.model_validate(chat).model_dump(),
            messages=[
                schemas.InterviewMessage.model_validate(m) for m in messages
            ],
        )

    async def list_chats_for_user(
        self, owner_id: uuid.UUID
    ) -> List[schemas.InterviewChat]:
        chats = await self.repo.list_chats_for_user(owner_id)
        return [schemas.InterviewChat.model_validate(c) for c in chats]

    async def delete_chat(
        self, chat_id: uuid.UUID, owner_id: uuid.UUID
    ) -> bool:
        chat = await self.repo.get_chat_by_id(chat_id, owner_id)
        if not chat:
            return False
        await self.repo.delete_chat(chat)
        return True

    async def send_message(
        self,
        chat_id: uuid.UUID,
        owner_id: uuid.UUID,
        content: str,
    ) -> schemas.InterviewMessageWithReply | None:
        chat = await self.repo.get_chat_by_id(chat_id, owner_id)
        if not chat:
            return None

        user_msg = await self.repo.add_message(
            chat_id=chat.id,
            role=MessageRole.USER,
            content=content,
        )

        messages = await self.repo.get_messages_for_chat(chat.id)
        history_messages = [
            {"role": m.role.value, "content": m.content} for m in messages
        ]

        system_prompt = {
            "role": "system",
            "content": (
                "You act like a strict but constructive interviewer. "
                "at the technical interview. Ask clarifying questions, "
                "evaluate the answers and give brief feedback."
            ),
        }
        history_for_reply = [system_prompt, *history_messages]

        ai_answer = await generate_interview_reply(history_for_reply)

        ai_msg = await self.repo.add_message(
            chat_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=ai_answer,
        )

        if not chat.title:
            try:
                title = await generate_chat_title(history_messages)
                await self.repo.update_title(chat, title)
            except Exception:
                pass

        return schemas.InterviewMessageWithReply(
            user_message=schemas.InterviewMessage.model_validate(user_msg),
            ai_message=schemas.InterviewMessage.model_validate(ai_msg),
        )