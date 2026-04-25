# app/routers/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, CurrentUser
from services.auth_service import register_user, login_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user (admin or student).
    Returns the created user info without the password.
    """
    return register_user(data, db)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email + password.
    Returns a JWT access token on success.
    """
    return login_user(data, db)


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Return the currently authenticated user's info.
    Requires a valid Bearer token.
    """
    return current_user
