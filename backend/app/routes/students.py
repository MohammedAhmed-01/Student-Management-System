from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.cache.cache_manager import cache_manager
from app.core.dependencies import get_current_user, get_db, require_admin
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Student:
    # Permission check: Admin can create for anyone, student only for themselves
    if current_user.role != "admin" and payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # Check if user exists
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if student already exists for this user
    existing = db.query(Student).filter(Student.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student record already exists for this user")

    # Check if university_id is unique
    existing_id = db.query(Student).filter(Student.university_id == payload.university_id).first()
    if existing_id:
        raise HTTPException(status_code=400, detail="University ID already exists")

    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    
    logger.info(f"Audit: Student created by User {current_user.id}. Student ID: {student.id}, University ID: {student.university_id}")
    
    # Invalidate list cache
    cache_manager.invalidate_prefix("students:list")
    
    return student


@router.get("/", response_model=list[StudentResponse])
def list_students(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    search: str | None = Query(None, description="Search by name or university ID"),
    department: str | None = None,
    status: str | None = None,
    gpa_min: float | None = Query(None, ge=0, le=4.0),
    gpa_max: float | None = Query(None, ge=0, le=4.0),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[Student]:
    query = db.query(Student)
    
    if search:
        query = query.filter(
            (Student.name.ilike(f"%{search}%")) | 
            (Student.university_id.ilike(f"%{search}%"))
        )
    if department:
        query = query.filter(Student.department == department)
    if status:
        query = query.filter(Student.status == status)
    if gpa_min is not None:
        query = query.filter(Student.gpa >= gpa_min)
    if gpa_max is not None:
        query = query.filter(Student.gpa <= gpa_max)
    
    students = query.order_by(Student.id).offset(skip).limit(limit).all()
    return students


@router.get("/me", response_model=StudentResponse)
def get_my_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Student:
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found for this user")
    return student


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Student:
    # Try cache first
    cache_key = f"students:detail:{student_id}"
    cached = cache_manager.get_json(cache_key)
    if cached:
        # Check permissions on cached data
        if current_user.role != "admin" and cached["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return Student(**cached)

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Permission check: Admin or the student themselves
    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Cache the result (convert to dict for JSON)
    student_data = {
        "id": student.id,
        "university_id": student.university_id,
        "name": student.name,
        "birth_date": student.birth_date.isoformat() if student.birth_date else None,
        "gender": student.gender,
        "phone_number": student.phone_number,
        "gpa": student.gpa,
        "department": student.department,
        "enrollment_date": student.enrollment_date.isoformat(),
        "status": student.status,
        "user_id": student.user_id
    }
    cache_manager.set_json(cache_key, student_data)
    
    return student


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Permission check: Admin or the student themselves
    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    
    logger.info(f"Audit: Student {student_id} updated by User {current_user.id}")
    
    # Invalidate caches
    cache_manager.invalidate_key(f"students:detail:{student_id}")
    cache_manager.invalidate_prefix("students:list")
    
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    
    logger.info(f"Audit: Student {student_id} deleted by User {current_user.id}")
    
    # Invalidate caches
    cache_manager.invalidate_key(f"students:detail:{student_id}")
    cache_manager.invalidate_prefix("students:list")


@router.get("/stats/summary")
def get_student_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Get a summary of student statistics.
    """
    total_students = db.query(Student).count()
    
    # Department breakdown
    dept_stats = db.query(
        Student.department, func.count(Student.id)
    ).group_by(Student.department).all()
    
    # Status breakdown
    status_stats = db.query(
        Student.status, func.count(Student.id)
    ).group_by(Student.status).all()
    
    # Average GPA
    avg_gpa = db.query(func.avg(Student.gpa)).scalar() or 0.0
    
    return {
        "total_students": total_students,
        "average_gpa": round(float(avg_gpa), 2),
        "departments": {dept: count for dept, count in dept_stats},
        "statuses": {status: count for status, count in status_stats}
    }
