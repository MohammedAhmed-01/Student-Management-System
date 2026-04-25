# app/services/student_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.student import Student
from models.user import User
from schemas.student import StudentCreate, StudentUpdate, StudentSelfUpdate
from schemas.auth import CurrentUser


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_student_or_404(student_id: int, db: Session) -> Student:
    """Fetch student by ID or raise 404."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found."
        )
    return student


def _assert_user_exists(user_id: int, db: Session) -> None:
    """Raise 404 if the linked user doesn't exist."""
    user = db.query(User).filter(User.user_id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found or inactive."
        )


def _assert_email_unique(email: str, db: Session, exclude_id: int = None) -> None:
    """Raise 409 if email already used by another student."""
    query = db.query(Student).filter(Student.email == email)
    if exclude_id:
        query = query.filter(Student.student_id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{email}' is already registered to another student."
        )


# ── Admin: CRUD ───────────────────────────────────────────────────────────────

def create_student(data: StudentCreate, db: Session) -> Student:
    """Admin: create a new student linked to an existing user."""
    _assert_user_exists(data.user_id, db)
    _assert_email_unique(data.email, db)

    # Make sure this user doesn't already have a student record
    existing = db.query(Student).filter(Student.user_id == data.user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {data.user_id} already has a student profile."
        )

    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_all_students(db: Session) -> list[Student]:
    """Admin: return all students (no filters — filters handled by member 4)."""
    return db.query(Student).all()


def get_student_by_id(student_id: int, db: Session) -> Student:
    """Admin: fetch any student by ID."""
    return _get_student_or_404(student_id, db)


def update_student(student_id: int, data: StudentUpdate, db: Session) -> Student:
    """Admin: fully update a student record."""
    student = _get_student_or_404(student_id, db)
    _assert_email_unique(data.email, db, exclude_id=student_id)

    for field, value in data.model_dump().items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(student_id: int, db: Session) -> None:
    """Admin: permanently delete a student record."""
    student = _get_student_or_404(student_id, db)
    db.delete(student)
    db.commit()


# ── Student: self-access ──────────────────────────────────────────────────────

def get_own_profile(current_user: CurrentUser, db: Session) -> Student:
    """Student: fetch their own profile only."""
    student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No student profile found for the current user."
        )
    return student


def update_own_profile(
    data: StudentSelfUpdate,
    current_user: CurrentUser,
    db: Session
) -> Student:
    """Student: partially update only their own allowed fields."""
    student = get_own_profile(current_user, db)

    # If email is being changed, check uniqueness
    if data.email and data.email != student.email:
        _assert_email_unique(data.email, db, exclude_id=student.student_id)

    # Only update fields that were actually provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student