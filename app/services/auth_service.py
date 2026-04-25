# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RegisterResponse
from core.security import hash_password, verify_password, create_access_token


def register_user(data: RegisterRequest, db: Session) -> RegisterResponse:
    """
    Register a new user.
    Raises 400 if email or username already exists.
    """
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken."
        )

    new_user = User(
        username        = data.username,
        email           = data.email,
        hashed_password = hash_password(data.password),
        role            = data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RegisterResponse.model_validate(new_user)


def login_user(data: LoginRequest, db: Session) -> TokenResponse:
    """
    Authenticate a user and return a JWT access token.
    Raises 401 on invalid credentials or inactive account.
    """
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive. Please contact support.",
        )

    token = create_access_token(data={
        "sub":  str(user.user_id),
        "role": user.role,
    })

    return TokenResponse(access_token=token)
