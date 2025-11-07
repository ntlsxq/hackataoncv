import logging
from fastapi import FastAPI, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, get_db

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



from .api.routers import service as service_router
from .api.routers import auth as auth_router
from .api import error_handler
# Include routers
app.add_exception_handler(RequestValidationError, error_handler.validation_exception_handler)
app.include_router(service_router.router, prefix="/api", tags=["service"])
app.include_router(auth_router.router, prefix="/api", tags=["auth"])
