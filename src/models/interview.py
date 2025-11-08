import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    UUID,
    ForeignKey,
    DateTime,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class InterviewChat(Base):
    __tablename__ = "interview_chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    title = Column(String, nullable=True)
    position = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner = relationship("User", backref="interview_chats")
    messages = relationship(
        "InterviewMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="InterviewMessage.created_at",
    )


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interview_chats.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("InterviewChat", back_populates="messages")