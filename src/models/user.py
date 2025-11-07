import uuid

from sqlalchemy import Column, String, UUID

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)

