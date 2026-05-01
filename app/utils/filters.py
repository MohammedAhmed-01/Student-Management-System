# app/utils/filters.py
# Member 4 - Filtering logic for GET /api/students/

from typing import Optional
from sqlalchemy.orm import Query
from models.student import Student


def apply_student_filters(
    query: Query,
    department:    Optional[str]   = None,
    gpa_min:       Optional[float] = None,
    gpa_max:       Optional[float] = None,
    status:        Optional[str]   = None,
    year_of_study: Optional[int]   = None,
) -> Query:
    """
    Apply optional filters to a SQLAlchemy Student query.

    Args:
        query:         Base SQLAlchemy query on Student.
        department:    Case-insensitive match on department name.
        gpa_min:       Minimum GPA (inclusive).
        gpa_max:       Maximum GPA (inclusive).
        status:        One of 'active', 'inactive', 'graduated'.
        year_of_study: Exact match on year of study (1-6).

    Returns:
        Filtered query (not yet executed).
    """
    if department is not None:
        query = query.filter(Student.department.ilike(department.strip()))

    if gpa_min is not None:
        query = query.filter(Student.gpa >= gpa_min)

    if gpa_max is not None:
        query = query.filter(Student.gpa <= gpa_max)

    if status is not None:
        query = query.filter(Student.status == status.strip().lower())

    if year_of_study is not None:
        query = query.filter(Student.year_of_study == year_of_study)

    return query
