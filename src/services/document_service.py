import asyncio
from typing import Optional, Dict, Any, List
from uuid import UUID

from src import models
from src.schemas import document_schemas as schemas
from src.repositories.document_repository import DocumentRepository
from src.utils import ai


class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    @staticmethod
    def _document_to_schema(doc: models.Document) -> schemas.DocumentResponse:
        current_version = None
        if doc.versions:
            current_version = doc.versions[-1]
        else:
            raise ValueError("Document has no versions")

        return schemas.DocumentResponse(
            id=doc.id,
            owner_id=doc.owner_id,
            current_version=doc.current_version,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            content=current_version.content,
        )

    async def create_document(
        self,
        owner_id: UUID,
        content: Dict[str, Any],
    ) -> schemas.DocumentResponse:
        doc = await self.document_repository.create_document(
            owner_id=owner_id,
            content=content,
        )
        return self._document_to_schema(doc)

    async def get_document(self, document_id: UUID) -> Optional[schemas.DocumentResponse]:
        doc = await self.document_repository.get_by_id(document_id)
        if not doc:
            return None
        return self._document_to_schema(doc)

    async def get_document_version(
        self,
        document_id: UUID,
        version_number: int,
    ) -> Optional[schemas.DocumentVersionResponse]:
        version = await self.document_repository.get_version(
            document_id=document_id,
            version_number=version_number,
        )
        if not version:
            return None

        return schemas.DocumentVersionResponse(
            version_number=version.version_number,
            content=version.content,
            created_at=version.created_at,
        )
    async def score_document(self,
                             document_id: UUID):
        doc = await self.document_repository.get_by_id(document_id)
        if not doc:
            return None
        content = doc.versions[doc.current_version - 1].content
        score, reason = await ai.score_resume_json(content)
        scored_content = {**content, "aimark": score, "reason": reason}

        await self.document_repository.update_version(
            document=doc,
            content=scored_content,
            version_number=doc.current_version,
        )

        return

    async def update_document(
        self,
        document_id: UUID,
        content: Dict[str, Any],
    ) -> Optional[schemas.DocumentResponse]:
        doc = await self.document_repository.get_by_id(document_id)
        if not doc:
            return None

        doc = await self.document_repository.create_new_version(
            document=doc,
            content=content,
        )

        asyncio.create_task(self.score_document(document_id))
        return self._document_to_schema(doc)

    async def delete_document(self, document_id: UUID) -> bool:
        await self.document_repository.delete(document_id)
        return True

    async def list_documents(self, owner_id: UUID) -> List[schemas.DocumentResponse]:
        docs = await self.document_repository.list_by_owner(owner_id)
        return [self._document_to_schema(doc) for doc in docs]