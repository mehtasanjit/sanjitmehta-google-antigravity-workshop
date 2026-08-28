from sqlalchemy.exc import IntegrityError
from app.errors import ConflictError, NotFoundError, ALREADY_ENROLLED, NOT_FOUND
from app.models import User, Course, Enrollment
from app.deps.auth import Principal
from app.services.audit import write_audit


def upsert_user(db, subject, role, display_name=None, email=None) -> User:
    user = db.query(User).filter(User.subject == subject).first()
    if user:
        if role is not None:
            user.role = role
        if display_name is not None:
            user.display_name = display_name
        if email is not None:
            user.email = email
    else:
        user = User(subject=subject, role=role, display_name=display_name, email=email)
        db.add(user)
    db.flush()
    return user


def create_course(db, principal: Principal, name, description=None) -> Course:
    # Ensure the owner's user row exists (users are created lazily); the course
    # FK owner_subject -> users.subject requires it before the insert.
    owner = db.query(User).filter(User.subject == principal.subject).first()
    if not owner:
        db.add(User(subject=principal.subject, role=principal.role))
        db.flush()
    course = Course(owner_subject=principal.subject, name=name, description=description)
    db.add(course)
    db.flush()
    write_audit(db, principal.subject, principal.role, 'course.create', 'course', course.id)
    return course


def list_courses_for_owner(db, owner_subject) -> list[Course]:
    return db.query(Course).filter(Course.owner_subject == owner_subject).order_by(Course.id).all()


def get_course(db, course_id) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFoundError(NOT_FOUND, 'Course not found')
    return course


def add_enrollment(db, principal, course: Course, student_subject) -> Enrollment:
    # Ensure the student's user row exists (users are created lazily); the
    # enrollment FK -> users.subject requires it before the insert.
    existing_user = db.query(User).filter(User.subject == student_subject).first()
    if not existing_user:
        db.add(User(subject=student_subject, role='student'))
        db.flush()
    enr = Enrollment(course_id=course.id, student_subject=student_subject)
    db.add(enr)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ConflictError(ALREADY_ENROLLED, 'Student already enrolled')
    write_audit(db, principal.subject, principal.role, 'enrollment.add', 'enrollment', enr.id)
    return enr


def remove_enrollment(db, principal, course, student_subject) -> None:
    enr = db.query(Enrollment).filter(
        Enrollment.course_id == course.id,
        Enrollment.student_subject == student_subject
    ).first()
    if not enr:
        raise NotFoundError(NOT_FOUND, 'Enrollment not found')
    enr_id = enr.id
    db.delete(enr)
    db.flush()
    write_audit(db, principal.subject, principal.role, 'enrollment.remove', 'enrollment', enr_id)


def list_enrollments(db, course_id) -> list[Enrollment]:
    return db.query(Enrollment).filter(Enrollment.course_id == course_id).order_by(Enrollment.id).all()
