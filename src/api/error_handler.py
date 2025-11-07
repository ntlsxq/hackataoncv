from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Invalid input data",
            "details": [
                {
                    "field": err["loc"][-1],
                    "message": err["ctx"]['reason']
                } for err in exc.errors()
            ],
        },
    )