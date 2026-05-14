from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class StudentBase(BaseModel):
    university_id: str
    name: str
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    gpa: float = Field(ge=0, le=4.0)
    department: str
    enrollment_date: date
    status: str = "active"

class StudentCreate(StudentBase):
    user_id: int

class StudentUpdate(BaseModel):
    university_id: Optional[str] = None
    name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0, le=4.0)
    department: Optional[str] = None
    enrollment_date: Optional[date] = None
    status: Optional[str] = None

class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
