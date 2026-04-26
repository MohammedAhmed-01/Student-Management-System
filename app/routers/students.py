# app/routers/students.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, require_admin
from schemas.student import StudentCreate, StudentUpdate, StudentSelfUpdate, StudentResponse
from schemas.auth import CurrentUser
from services import student_service

router = APIRouter(prefix="/api/students", tags=["Students"])


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

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
    **Admin only.**  
    Create a student profile linked to an existing user account.
    """
    return student_service.create_student(data, db)


@router.get(
    "/",
    response_model=list[StudentResponse],
    summary="[Admin] List all students",
)
def list_students(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    """
    **Admin only.**  
    Return all student records.  
    Filtering and pagination are handled by Member 4's query parameters.
    """
    return student_service.get_all_students(db)


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
    **Admin only.**  
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
    **Admin only.**  
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
    **Admin only.**  
    Permanently remove a student record.
    """
    student_service.delete_student(student_id, db)


# ══════════════════════════════════════════════════════════════════════════════
#  STUDENT SELF-ACCESS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

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
    **Student only.**  
    Returns the profile of the currently authenticated student.  
    A student cannot access any other student's data.
    """
    if current_user.role != "student":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint."
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
    **Student only.**  
    Allowed fields: `phone`, `address`, `email`.  
    Any attempt to update restricted fields (e.g. GPA, department) will be rejected.
    """
    if current_user.role != "student":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint."
        )
    return student_service.update_own_profile(data, current_user, db)