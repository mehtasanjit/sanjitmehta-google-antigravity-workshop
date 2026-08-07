"""Authorization: deny-by-default rules combining SCOPE + OWNERSHIP.

Every rule requires two things to pass:
  1. scope check  — did the user consent to this class of action?
  2. ownership     — does THIS user own/teach THIS specific resource?

This is where the "on behalf of" guarantee is enforced: results are always
filtered to what the authenticated principal is allowed to see.
"""
from fastapi import HTTPException, status

from .models import Principal
from .store import NotFound, Store

# Scope constants
READ_SELF = "grades.read.self"
READ_COURSE = "grades.read.course"
WRITE_COURSE = "grades.write.course"


def _forbid(msg: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)


def _not_found(msg: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


def read_student_grades(principal: Principal, student_id: str, store: Store) -> list[dict]:
    """A student reads their own; a professor reads only their taught courses'
    slice of that student; an admin reads everything."""
    try:
        store.student(student_id)
    except NotFound as e:
        raise _not_found(str(e))

    if principal.role == "admin":
        return store.grades_for_student(student_id)

    if principal.role == "student":
        if principal.sub != student_id:
            raise _forbid("Students may only read their own grades")
        if not principal.has_scope(READ_SELF):
            raise _forbid(f"Missing scope {READ_SELF}")
        return store.grades_for_student(student_id)

    if principal.role == "professor":
        if not principal.has_scope(READ_COURSE):
            raise _forbid(f"Missing scope {READ_COURSE}")
        taught = store.courses_taught_by(principal.sub)
        visible = taught & store.courses_for_student(student_id)
        if not visible:
            raise _forbid("You do not teach any course this student is enrolled in")
        return store.grades_for_student(student_id, only_courses=visible)

    raise _forbid("Not authorized")


def read_course_grades(principal: Principal, course_code: str, store: Store) -> list[dict]:
    """A professor reads a course they own; an admin reads any course."""
    try:
        course = store.course(course_code)
    except NotFound as e:
        raise _not_found(str(e))

    if principal.role == "admin":
        return store.grades_for_course(course_code)

    if principal.role == "professor":
        if not principal.has_scope(READ_COURSE):
            raise _forbid(f"Missing scope {READ_COURSE}")
        if course["professor_id"] != principal.sub:
            raise _forbid("You do not teach this course")
        return store.grades_for_course(course_code)

    raise _forbid("Only professors (of this course) or admins may read course grades")


def write_course_grade(
    principal: Principal, course_code: str, student_id: str, score: float, store: Store
) -> dict:
    """A professor writes grades for a course they own; an admin for any."""
    try:
        course = store.course(course_code)
    except NotFound as e:
        raise _not_found(str(e))

    if principal.role == "admin":
        return store.upsert_grade(student_id, course_code, score, updated_by=principal.sub)

    if principal.role == "professor":
        if not principal.has_scope(WRITE_COURSE):
            raise _forbid(f"Missing scope {WRITE_COURSE}")
        if course["professor_id"] != principal.sub:
            raise _forbid("You do not teach this course")
        if not store.is_enrolled(student_id, course_code):
            raise _forbid("Student is not enrolled in this course")
        return store.upsert_grade(student_id, course_code, score, updated_by=principal.sub)

    raise _forbid("Only professors (of this course) or admins may write grades")


def list_courses(principal: Principal, store: Store) -> list[dict]:
    """Course list, filtered to the caller's identity."""
    if principal.role == "admin":
        codes = set(store.courses.keys())
    elif principal.role == "professor":
        codes = store.courses_taught_by(principal.sub)
    else:  # student
        codes = store.courses_for_student(principal.sub)
    return [store.course_view(c) for c in sorted(codes)]
