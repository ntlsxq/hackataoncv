from typing import Dict, Any

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

def _get_field_from_loc(loc: tuple[Any, ...]) -> str:
    """
    loc = ('body', 'user', 'email') -> 'user.email'
    loc = ('body', 'name') -> 'name'
    loc = ('query', 'limit') -> 'limit'
    loc = ('body',) -> 'body'
    """
    if not loc:
        return "non_field_error"

    # убираем первый элемент (body/query/path/header/cookie), если он служебный
    first = str(loc[0])
    if first in {"body", "query", "path", "header", "cookie"}:
        loc = loc[1:]

    if not loc:
        return first

    return ".".join(str(x) for x in loc)


def _format_validation_error(err: Dict[str, Any]) -> Dict[str, Any]:
    field = _get_field_from_loc(err.get("loc", ()))
    ctx = err.get("ctx") or {}

    # приоритет: ctx["reason"] (если ты сам его передаёшь в кастомных валидациях)
    message = ctx.get("reason") or err.get("msg", "Invalid value")

    return {
        "field": field,
        "message": message,
        "type": err.get("type"),
    }


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Для дебага:
    # print(exc.errors())
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid input data",
            "details": [
                _format_validation_error(err) for err in exc.errors()
            ],
        },
    )