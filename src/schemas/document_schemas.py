import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class DocumentCreateRequest(BaseModel):
    content: Dict[str, Any]


class DocumentUpdateRequest(BaseModel):
    content: Dict[str, Any]


class DocumentVersionResponse(BaseModel):
    version_number: int
    content: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    current_version: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    content: Dict[str, Any]

    class Config:
        from_attributes = True