# src/routers/document_router.py (или src/api/routes/documents.py)
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies.auth import get_current_user
from src.dependencies.misc import get_document_service
from src.schemas.user_schemas import User
from src.schemas import document_schemas as schemas
from src.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=schemas.DocumentResponse)
async def create_document(
    body: schemas.DocumentCreateRequest,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    doc = await document_service.create_document(
        owner_id=current_user.id,
        content=body.content,
    )
    return doc

@router.get("/", response_model=List[schemas.DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    return await document_service.list_documents(owner_id=current_user.id)

@router.get("/{document_id}", response_model=schemas.DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    doc = await document_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )
    return doc


@router.put("/{document_id}", response_model=schemas.DocumentResponse)
async def update_document(
    document_id: UUID,
    body: schemas.DocumentUpdateRequest,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    doc = await document_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    updated = await document_service.update_document(
        document_id=document_id,
        content=body.content,
    )
    return updated


@router.get(
    "/{document_id}/versions/{version_number}",
    response_model=schemas.DocumentVersionResponse,
)
async def get_document_version(
    document_id: UUID,
    version_number: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    doc = await document_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    version = await document_service.get_document_version(
        document_id=document_id,
        version_number=version_number,
    )
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )
    return version


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    doc = await document_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    await document_service.delete_document(document_id)
    return {"success": True}