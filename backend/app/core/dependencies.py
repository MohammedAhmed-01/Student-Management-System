from collections.abc import Callable, Iterable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme
from app.db.session import get_db
from app.models.user import User
from app.utils.jwt import verify_access_token

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

_forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions",
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = verify_access_token(token)
    except ValueError as exc:
        raise _credentials_exception from exc

    sub = payload.get("sub")
    if sub is None:
        raise _credentials_exception

    email = sub if isinstance(sub, str) else str(sub)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    token_role = payload.get("role")
    if token_role is not None and token_role != user.role:
        raise _credentials_exception

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise _forbidden_exception
    return current_user


def require_student(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "student":
        raise _forbidden_exception
    return current_user


def require_roles(allowed_roles: Iterable[str]) -> Callable[..., User]:
    allowed = frozenset(allowed_roles)

    def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed:
            raise _forbidden_exception
        return current_user

    return role_dependency
