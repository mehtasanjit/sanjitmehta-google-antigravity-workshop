from fastapi import FastAPI
from app.config import get_settings
from app.logging_config import configure_logging
from app.db import Base, get_engine
import app.models  # noqa: F401
from app.middleware.request_context import RequestContextMiddleware
from app.errors import register_error_handlers
from app.routers import auth, courses, sessions, polls, questions, pulse


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(title='Lecture Pulse', version='1.0.0')
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)
    # create tables at startup
    Base.metadata.create_all(bind=get_engine())
    for r in (auth.router, courses.router, sessions.router, polls.router, questions.router, pulse.router):
        app.include_router(r)

    @app.get('/health', tags=['health'])
    def health():
        return {'status': 'ok'}

    return app


app = create_app()
