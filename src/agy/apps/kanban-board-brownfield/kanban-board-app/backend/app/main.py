"""FastAPI application: CORS, error mapping, and startup initialisation."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import service
from app.api import router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    service.initialize()
    yield


app = FastAPI(title="Kanban Board API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(service.NotFoundError)
async def not_found_handler(_: Request, exc: service.NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(service.InvalidMoveError)
async def invalid_move_handler(_: Request, exc: service.InvalidMoveError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": str(exc)}
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Flatten Pydantic errors into one readable message: {"detail": "<message>"}."""
    messages = []
    for error in exc.errors():
        field = ".".join(str(part) for part in error["loc"] if part != "body")
        message = error["msg"].removeprefix("Value error, ")
        messages.append(f"{field}: {message}" if field else message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": "; ".join(messages)}
    )


app.include_router(router)
