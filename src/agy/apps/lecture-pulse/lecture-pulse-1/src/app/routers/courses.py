from fastapi import APIRouter, Depends
from app.db import get_db
from app.deps.auth import require_role, get_current_principal
from app.deps.access import require_course_owner
from app.schemas.common import ListResponse
from app.schemas.course import CourseCreate, CourseOut, EnrollmentCreate, EnrollmentOut
from app.schemas.session import SessionCreate, SessionOut
from app.services.courses import create_course, list_courses_for_owner, add_enrollment, remove_enrollment, list_enrollments
from app.services.sessions import create_session, list_sessions

router = APIRouter(prefix='/courses', tags=['courses'])


@router.post('', response_model=CourseOut, status_code=201)
def create(body: CourseCreate, db=Depends(get_db), principal=Depends(require_role('instructor'))):
    return create_course(db, principal, body.name, body.description)


@router.get('', response_model=ListResponse[CourseOut])
def list_courses(db=Depends(get_db), principal=Depends(require_role('instructor'))):
    return {"items": list_courses_for_owner(db, principal.subject)}


@router.get('/{course_id}', response_model=CourseOut)
def get_course_route(course=Depends(require_course_owner)):
    return course


@router.post('/{course_id}/enrollments', response_model=EnrollmentOut, status_code=201)
def enroll(body: EnrollmentCreate, db=Depends(get_db), course=Depends(require_course_owner), principal=Depends(get_current_principal)):
    return add_enrollment(db, principal, course, body.student_subject)


@router.delete('/{course_id}/enrollments/{student_subject}', status_code=204)
def unenroll(student_subject: str, db=Depends(get_db), course=Depends(require_course_owner), principal=Depends(get_current_principal)):
    remove_enrollment(db, principal, course, student_subject)
    return None


@router.get('/{course_id}/enrollments', response_model=ListResponse[EnrollmentOut])
def list_enr(db=Depends(get_db), course=Depends(require_course_owner)):
    return {"items": list_enrollments(db, course.id)}


@router.post('/{course_id}/sessions', response_model=SessionOut, status_code=201)
def create_sess(body: SessionCreate, db=Depends(get_db), course=Depends(require_course_owner), principal=Depends(get_current_principal)):
    return create_session(db, principal, course, body.title)


@router.get('/{course_id}/sessions', response_model=ListResponse[SessionOut])
def list_sess(db=Depends(get_db), course=Depends(require_course_owner)):
    return {"items": list_sessions(db, course.id)}
