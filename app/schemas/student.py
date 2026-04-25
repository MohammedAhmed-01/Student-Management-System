# app/schemas/student.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Shared base ───────────────────────────────────────────────────────────────

class StudentBase(BaseModel):
    first_name:      str            = Field(..., min_length=1, max_length=100)
    last_name:       str            = Field(..., min_length=1, max_length=100)
    email:           EmailStr
    phone:           Optional[str]  = Field(None, max_length=20)
    date_of_birth:   Optional[date] = None
    gender:          Optional[str]  = Field(None, pattern="^(male|female|other)$")
    department:      str            = Field(..., min_length=1, max_length=100)
    major:           str            = Field(..., min_length=1, max_length=100)
    enrollment_year: int            = Field(..., ge=2000, le=2100)
    year_of_study:   int            = Field(..., ge=1, le=6)
    gpa:             Optional[Decimal] = Field(None, ge=0, le=4)
    status:          Optional[str]  = Field("active", pattern="^(active|inactive|graduated)$")
    address:         Optional[str]  = Field(None, max_length=500)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


# ── Admin: Create a new student (requires user_id) ───────────────────────────

class StudentCreate(StudentBase):
    """Used by admin to create a student record linked to an existing user."""
    user_id: int


# ── Admin: Full update ────────────────────────────────────────────────────────

class StudentUpdate(StudentBase):
    """Admin can update any field."""
    pass


# ── Student: Partial self-update (only allowed fields) ───────────────────────

class StudentSelfUpdate(BaseModel):
    """
    A student can only update their own contact info.
    All fields are optional — only provided fields will be updated.
    """
    phone:         Optional[str]     = Field(None, max_length=20)
    address:       Optional[str]     = Field(None, max_length=500)
    email:         Optional[EmailStr] = None

    model_config = {"extra": "forbid"}  # block attempts to sneak in other fields


# ── Response model ────────────────────────────────────────────────────────────

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

    model_config = {"from_attributes": True}  # allows ORM → schema conversion