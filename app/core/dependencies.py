# app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_access_token
from models.user import User
from schemas.auth import CurrentUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """
    Decode the JWT, load the matching User row, and return a CurrentUser.
    Raises 401 if the token is invalid/expired or the user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(
        User.user_id == int(user_id),
        User.is_active == True
    ).first()
    if user is None:
        raise credentials_exception

    return CurrentUser.model_validate(user)


# ── Role-based authorization ──────────────────────────────────────────────────

def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Allow only admins."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
    return current_user


def require_student(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Allow only students."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required."
        )
    return current_user


def require_admin_or_student(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Allow both admins and students (any authenticated user)."""
    if current_user.role not in ("admin", "student"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    return current_user
