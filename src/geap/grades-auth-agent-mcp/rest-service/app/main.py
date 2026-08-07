"""FastAPI app for the grades REST service.

The resource server at the bottom of the OBO chain: it validates the forwarded
user token and enforces per-user authorization on every grade it returns.
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from . import authz, config
from .auth import verify_token
from .models import Course, Grade, GradeUpsert, Principal
from .store import Store


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = Store.from_file(config.DATA_PATH)
    yield


app = FastAPI(
    title="Grades REST Service",
    version="0.1.0",
    description="Token-authenticated grades API with per-user (on-behalf-of) authorization.",
    lifespan=lifespan,
)


def get_store() -> Store:
    return app.state.store


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Liveness probe (public — used by Cloud Run)."""
    return {"status": "ok"}


@app.get("/me", tags=["meta"])
def me(principal: Principal = Depends(verify_token)) -> Principal:
    """Echo the caller's identity from the validated token — proves who the
    request is acting *on behalf of*."""
    return principal


@app.get("/courses", response_model=list[Course], tags=["courses"])
def list_courses(
    principal: Principal = Depends(verify_token),
    store: Store = Depends(get_store),
) -> list[dict]:
    return authz.list_courses(principal, store)


@app.get("/students/{student_id}/grades", response_model=list[Grade], tags=["grades"])
def student_grades(
    student_id: str,
    principal: Principal = Depends(verify_token),
    store: Store = Depends(get_store),
) -> list[dict]:
    return authz.read_student_grades(principal, student_id, store)


@app.get("/courses/{course_code}/grades", response_model=list[Grade], tags=["grades"])
def course_grades(
    course_code: str,
    principal: Principal = Depends(verify_token),
    store: Store = Depends(get_store),
) -> list[dict]:
    return authz.read_course_grades(principal, course_code, store)


@app.post("/courses/{course_code}/grades", response_model=Grade, tags=["grades"])
def upsert_course_grade(
    course_code: str,
    body: GradeUpsert,
    principal: Principal = Depends(verify_token),
    store: Store = Depends(get_store),
) -> dict:
    return authz.write_course_grade(
        principal, course_code, body.student_id, body.score, store
    )
