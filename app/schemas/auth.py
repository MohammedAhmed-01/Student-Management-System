# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field


# ── Registration ──────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str      = Field(..., min_length=3, max_length=50)
    email:    EmailStr
    password: str      = Field(..., min_length=6)
    role:     str      = Field(default="student", pattern="^(admin|student)$")


class RegisterResponse(BaseModel):
    user_id:  int
    username: str
    email:    str
    role:     str

    model_config = {"from_attributes": True}


# ── Login ─────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ── Current user (returned by get_current_user dependency) ────────────────────
class CurrentUser(BaseModel):
    user_id:  int
    username: str
    email:    str
    role:     str

    model_config = {"from_attributes": True}
