from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.document_repository import DocumentRepository
from src.repositories.user_repository import UserRepository
from src.services.document_service import DocumentService
from src.services.user_service import UserService


async def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)

async def get_document_repository(session: AsyncSession = Depends(get_db),) -> DocumentRepository:
    return DocumentRepository(session)

async def get_document_service(
document_repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentService:
    return DocumentService(document_repository)