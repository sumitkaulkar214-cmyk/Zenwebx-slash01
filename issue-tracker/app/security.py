from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.auth import decode_token
from app.database import get_db
from app.models import User

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt. Never store plain passwords."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT bearer dependencies
# ---------------------------------------------------------------------------
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency. Validates the Bearer token in the Authorization header.
    Returns the User object for the authenticated caller.
    Raises 401 if token is missing, expired, or invalid.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token payload malformed")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency. Requires the authenticated user to have the 'admin' role.
    Raises 403 Forbidden if they are a regular member.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
