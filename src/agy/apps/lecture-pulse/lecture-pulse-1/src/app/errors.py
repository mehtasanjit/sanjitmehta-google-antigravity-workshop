import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)

# Error code constants (stable machine strings)
DUPLICATE_RESPONSE = "duplicate_response"
DUPLICATE_UPVOTE = "duplicate_upvote"
DUPLICATE_RATING = "duplicate_rating"
POLL_CLOSED = "poll_closed"
ILLEGAL_TRANSITION = "illegal_transition"
NOT_ENROLLED = "not_enrolled"
NOT_JOINED = "not_joined"
FORBIDDEN = "forbidden"
UNAUTHORIZED = "unauthorized"
NOT_FOUND = "not_found"
VALIDATION_ERROR = "validation_error"
SESSION_NOT_ACTIVE = "session_not_active"
ALREADY_ENROLLED = "already_enrolled"
ALREADY_UPVOTED = "already_upvoted"


class AppError(Exception):
    def __init__(self, code: str, message: str, http_status: int, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details


class AuthError(AppError):
    def __init__(self, code: str = UNAUTHORIZED, message: str = "Unauthorized", details=None):
        super().__init__(code=code, message=message, http_status=401, details=details)


class ForbiddenError(AppError):
    def __init__(self, code: str = FORBIDDEN, message: str = "Forbidden", details=None):
        super().__init__(code=code, message=message, http_status=403, details=details)


class NotFoundError(AppError):
    def __init__(self, code: str = NOT_FOUND, message: str = "Not found", details=None):
        super().__init__(code=code, message=message, http_status=404, details=details)


class ConflictError(AppError):
    def __init__(self, code: str, message: str, details=None):
        super().__init__(code=code, message=message, http_status=409, details=details)


class ValidationAppError(AppError):
    def __init__(self, code: str = VALIDATION_ERROR, message: str = "Validation failed", details=None):
        super().__init__(code=code, message=message, http_status=422, details=details)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": VALIDATION_ERROR,
                    "message": "Validation failed",
                    "details": jsonable_encoder(exc.errors())
                }
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception occurred: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Internal server error",
                    "details": None
                }
            }
        )
