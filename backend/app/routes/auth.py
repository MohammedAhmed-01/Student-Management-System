from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == str(payload.email)).first()
    if existing:
        logger.warning(f"Registration failed: Email {payload.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=str(payload.email),
        password=hash_password(payload.password),
        full_name=payload.full_name,
        role="student",  # Force student role for public registration
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: {user.email} (Role: {user.role})")
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == str(payload.email)).first()
    if user is None or not verify_password(payload.password, user.password):
        logger.warning(f"Login failed: Invalid credentials for {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
    )
    logger.info(f"User logged in successfully: {user.email}")
    return Token(access_token=access_token, token_type="bearer")
