from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import models


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(
        self,
        owner_id: UUID,
        content: Dict[str, Any],
    ) -> models.Document:
        doc = models.Document(owner_id=owner_id, current_version=1)
        self.session.add(doc)
        await self.session.flush()

        version = models.DocumentVersion(
            document_id=doc.id,
            version_number=1,
            content=content,
        )
        self.session.add(version)
        await self.session.commit()

        query = (
            select(models.Document)
            .options(selectinload(models.Document.versions))
            .where(models.Document.id == doc.id)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, document_id: UUID) -> Optional[models.Document]:
        stmt = (
            select(models.Document)
            .options(selectinload(models.Document.versions))
            .where(models.Document.id == document_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_version(
        self,
        document_id: UUID,
        version_number: int,
    ) -> Optional[models.DocumentVersion]:
        query = select(models.DocumentVersion).where(
            models.DocumentVersion.document_id == document_id,
            models.DocumentVersion.version_number == version_number,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_new_version(
        self,
        document: models.Document,
        content: Dict[str, Any],
    ) -> models.Document:
        document.current_version += 1
        new_version_number = document.current_version

        version = models.DocumentVersion(
            document_id=document.id,
            version_number=new_version_number,
            content=content,
        )
        self.session.add(version)
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def delete(self, document_id: UUID) -> None:
        doc = await self.get_by_id(document_id)
        if doc:
            await self.session.delete(doc)
            await self.session.commit()

    async def list_by_owner(self, owner_id: UUID) -> List[models.Document]:
        query = (
            select(models.Document)
            .options(selectinload(models.Document.versions))
            .where(models.Document.owner_id == owner_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().unique().all())