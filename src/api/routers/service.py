from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def test():
    return "pong"