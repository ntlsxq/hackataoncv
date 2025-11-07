import logging
from fastapi import FastAPI, Depends, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, get_db
from .api.routers import test as test_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CV",
    description="CV",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)




# Include routers
app.include_router(test_router.router, prefix="/api", tags=["chat"])


@app.on_event("startup")
async def startup_event():
    # Create database tables
    logger.info("Creating database tables if they don't exist")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



@app.get("/")
async def root():
    return {"message": "Support Chat API"}