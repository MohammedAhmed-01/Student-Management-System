from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.models.student import Student
from app.models.user import User
from app.utils.hashing import hash_password


from datetime import date

def seed_user(db: Session, email: str, password: str, role: str, full_name: str) -> User:
    existing_user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    
    if existing_user:
        existing_user.password = hash_password(password)
        existing_user.role = role
        existing_user.full_name = full_name
        db.commit()
        return existing_user

    user = User(
        email=email,
        password=hash_password(password),
        role=role,
        full_name=full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_data(db: Session) -> None:
    # 1. Seed Admin User
    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    seed_user(db, admin_email, admin_password, "admin", "System Administrator")

    # 2. Seed Student User
    student_email = os.getenv("SEED_USER_EMAIL", "student@example.com")
    student_password = os.getenv("SEED_USER_PASSWORD", "password123")
    student_name = os.getenv("SEED_STUDENT_NAME", "Sample Student")
    
    user = seed_user(db, student_email, student_password, "student", student_name)

    # 3. Seed Student Profile
    existing_student = db.execute(
        select(Student).where(Student.user_id == user.id)
    ).scalar_one_or_none()

    if not existing_student:
        university_id = os.getenv("SEED_UNIVERSITY_ID", "STU-001")
        gpa = float(os.getenv("SEED_STUDENT_GPA", "3.5"))
        department = os.getenv("SEED_STUDENT_DEPARTMENT", "Computer Science")

        student = Student(
            name=student_name,
            gpa=gpa,
            department=department,
            user_id=user.id,
            university_id=university_id,
            enrollment_date=date.today(),
            status="active"
        )
        db.add(student)
        db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed_data(db)


if __name__ == "__main__":
    main()
