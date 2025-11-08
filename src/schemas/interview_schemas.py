import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.models.interview import MessageRole


class InterviewMessageBase(BaseModel):
    role: MessageRole
    content: str


class InterviewMessageCreate(BaseModel):
    content: str


class InterviewMessage(InterviewMessageBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewChatCreate(BaseModel):
    title: Optional[str] = None
    position: Optional[str] = None


class InterviewChat(BaseModel):
    id: uuid.UUID
    title: Optional[str] = None
    position: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewChatDetail(InterviewChat):
    messages: List[InterviewMessage]


class InterviewMessageWithReply(BaseModel):
    user_message: InterviewMessage
    ai_message: InterviewMessage