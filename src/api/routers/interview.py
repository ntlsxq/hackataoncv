import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.user_schemas import User
from src.schemas import interview_schemas as schemas
from src.dependencies.auth import get_current_user
from src.dependencies.misc import get_interview_chat_service
from src.services.interview_service import InterviewChatService

router = APIRouter(prefix="/interview", tags=["interview-chat"])


@router.post("/chats", response_model=schemas.InterviewChat)
async def create_chat(
    chat_in: schemas.InterviewChatCreate,
    current_user: User = Depends(get_current_user),
    service: InterviewChatService = Depends(get_interview_chat_service),
):

    chat = await service.create_chat(
        owner_id=current_user.id,
        title=chat_in.title,
        position=chat_in.position,
    )
    return chat


@router.get("/chats", response_model=List[schemas.InterviewChat])
async def list_chats(
    current_user: User = Depends(get_current_user),
    service: InterviewChatService = Depends(get_interview_chat_service),
):

    return await service.list_chats_for_user(owner_id=current_user.id)


@router.get("/chats/{chat_id}", response_model=schemas.InterviewChatDetail)
async def get_chat(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewChatService = Depends(get_interview_chat_service),
):
    chat = await service.get_chat_detail(chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewChatService = Depends(get_interview_chat_service),
):
    ok = await service.delete_chat(chat_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return


@router.post(
    "/chats/{chat_id}/messages",
    response_model=schemas.InterviewMessageWithReply,
)
async def send_message(
    chat_id: uuid.UUID,
    message_in: schemas.InterviewMessageCreate,
    current_user: User = Depends(get_current_user),
    service: InterviewChatService = Depends(get_interview_chat_service),
):

    res = await service.send_message(
        chat_id=chat_id,
        owner_id=current_user.id,
        content=message_in.content,
    )
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return res