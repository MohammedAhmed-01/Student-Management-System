# app/routers/students.py
# Member 4 - Updated GET /api/students/ with filtering + pagination
# All other endpoints remain exactly as Member 3 left them.

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, require_admin
from models.student import Student
from schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentSelfUpdate,
    StudentResponse,
    PaginatedStudentResponse,
)
from schemas.auth import CurrentUser
from services import student_service
from utils.filters import apply_student_filters
from utils.pagination import paginate_query, calc_pages

router = APIRouter(prefix="/api/students", tags=["Students"])


# ============================================================
#  ADMIN ENDPOINTS
# ============================================================

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Create a new student",
)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    """
    Admin only.
    Create a student profile linked to an existing user account.
    """
    return student_service.create_student(data, db)


@router.get(
    "/",
    response_model=PaginatedStudentResponse,
    summary="[Admin] List students with filtering and pagination",
)
def list_students(
    # Filtering params
    department:    Optional[str]   = Query(default=None, description="Filter by department name (case-insensitive)"),
    gpa_min:       Optional[float] = Query(default=None, ge=0.0, le=4.0, description="Minimum GPA (inclusive)"),
    gpa_max:       Optional[float] = Query(default=None, ge=0.0, le=4.0, description="Maximum GPA (inclusive)"),
    status:        Optional[str]   = Query(default=None, pattern="^(active|inactive|graduated)$", description="Enrollment status"),
    year_of_study: Optional[int]   = Query(default=None, ge=1, le=6, description="Year of study (1-6)"),
    # Pagination params
    page:          int             = Query(default=1,  ge=1,        description="Page number (1-based)"),
    page_size:     int             = Query(default=10, ge=1, le=100, description="Items per page (max 100)"),
    # Dependencies
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    """
    Admin only. Return a paginated list of students with optional filters.

    Filtering:
    - department: case-insensitive match
    - gpa_min / gpa_max: inclusive GPA range (0.0 - 4.0)
    - status: active, inactive, or graduated
    - year_of_study: 1 through 6

    Pagination:
    - page: page number, starts at 1
    - page_size: records per page, max 100

    Example requests:
        GET /api/students/
        GET /api/students/?department=CS&page=1&page_size=20
        GET /api/students/?gpa_min=3.5&status=active
        GET /api/students/?department=Engineering&gpa_min=2.0&gpa_max=3.5&year_of_study=3&page=2

    Response format:
        {
          "total": 150,
          "page": 1,
          "page_size": 10,
          "pages": 15,
          "data": [ ... ]
        }
    """
    if gpa_min is not None and gpa_max is not None and gpa_min > gpa_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="gpa_min cannot be greater than gpa_max.",
        )

    query = db.query(Student)

    query = apply_student_filters(
        query,
        department=department,
        gpa_min=gpa_min,
        gpa_max=gpa_max,
        status=status,
        year_of_study=year_of_study,
    )

    query = query.order_by(Student.student_id)

    items, total = paginate_query(query, page=page, page_size=page_size)

    return PaginatedStudentResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=calc_pages(total, page_size),
        data=items,
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="[Admin] Get student by ID",
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    """
    Admin only.
    Retrieve a single student by their ID.
    """
    return student_service.get_student_by_id(student_id, db)


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="[Admin] Fully update a student",
)
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    """
    Admin only.
    Replace all updatable fields on a student record.
    """
    return student_service.update_student(student_id, data, db)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a student",
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    """
    Admin only.
    Permanently remove a student record.
    """
    student_service.delete_student(student_id, db)


# ============================================================
#  STUDENT SELF-ACCESS ENDPOINTS
# ============================================================

@router.get(
    "/me/profile",
    response_model=StudentResponse,
    summary="[Student] View own profile",
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Student only.
    Returns the profile of the currently authenticated student.
    A student cannot access any other student's data.
    """
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint.",
        )
    return student_service.get_own_profile(current_user, db)


@router.patch(
    "/me/profile",
    response_model=StudentResponse,
    summary="[Student] Partially update own profile",
)
def update_my_profile(
    data: StudentSelfUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Student only.
    Allowed fields: phone, address, email.
    Any attempt to update restricted fields will be rejected.
    """
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint.",
        )
    return student_service.update_own_profile(data, current_user, db)
