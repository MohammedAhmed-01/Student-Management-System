# app/schemas/student.py
# Member 4 - Added PaginatedStudentResponse to existing schemas

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class StudentBase(BaseModel):
    first_name:      str               = Field(..., min_length=1, max_length=100)
    last_name:       str               = Field(..., min_length=1, max_length=100)
    email:           EmailStr
    phone:           Optional[str]     = Field(None, max_length=20)
    date_of_birth:   Optional[date]    = None
    gender:          Optional[str]     = Field(None, pattern="^(male|female|other)$")
    department:      str               = Field(..., min_length=1, max_length=100)
    major:           str               = Field(..., min_length=1, max_length=100)
    enrollment_year: int               = Field(..., ge=2000, le=2100)
    year_of_study:   int               = Field(..., ge=1, le=6)
    gpa:             Optional[Decimal] = Field(None, ge=0, le=4)
    status:          Optional[str]     = Field("active", pattern="^(active|inactive|graduated)$")
    address:         Optional[str]     = Field(None, max_length=500)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class StudentCreate(StudentBase):
    user_id: int


class StudentUpdate(StudentBase):
    pass


class StudentSelfUpdate(BaseModel):
    phone:   Optional[str]      = Field(None, max_length=20)
    address: Optional[str]      = Field(None, max_length=500)
    email:   Optional[EmailStr] = None

    model_config = {"extra": "forbid"}


class StudentResponse(BaseModel):
    student_id:      int
    user_id:         int
    first_name:      str
    last_name:       str
    email:           str
    phone:           Optional[str]
    date_of_birth:   Optional[date]
    gender:          Optional[str]
    department:      str
    major:           str
    enrollment_year: int
    year_of_study:   int
    gpa:             Optional[Decimal]
    status:          str
    address:         Optional[str]
    created_at:      datetime
    updated_at:      Optional[datetime]

    model_config = {"from_attributes": True}


class PaginatedStudentResponse(BaseModel):
    """
    Paginated list of students returned by GET /api/students/
    """
    total:     int                   # Total matching students in DB
    page:      int                   # Current page (1-indexed)
    page_size: int                   # Records per page
    pages:     int                   # Total number of pages
    data:      List[StudentResponse] # Students on this page

    model_config = {"from_attributes": True}
