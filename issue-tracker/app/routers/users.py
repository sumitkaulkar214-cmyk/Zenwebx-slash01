# All user responses use UserPublic which never exposes hashed_password
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.auth import create_access_token, create_refresh_token, decode_token
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, RefreshRequest, TokenResponse, UserCreate, UserPublic, UserRegister
from app.security import get_current_user, hash_password, require_admin, verify_password
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Users"])


# ---------------------------------------------------------------------------
# Endpoint A — Public self-registration (no auth required)
# ---------------------------------------------------------------------------
@router.post(
    "/auth/register",
    response_model=UserPublic,
    status_code=201,
    summary="Register a new account (public — no auth required)",
)
# Rate limited: max 5 registrations per minute per IP
@limiter.limit("5/minute")
def register(request: Request, user_in: UserRegister, db: Session = Depends(get_db)):
    # 1. Check email uniqueness
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. First user automatically becomes admin
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "member"

    # 3. Create user — plain password is never stored or logged
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---------------------------------------------------------------------------
# Endpoint B — Admin creates a user with explicit role
# ---------------------------------------------------------------------------
@router.post(
    "/users",
    response_model=UserPublic,
    status_code=201,
    summary="Admin: create a user with explicit role (auth required — enforced in later chunk)",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash before saving — plain user_in.password must NEVER be stored or logged
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------
@router.get("/users", response_model=List[UserPublic], summary="List all users")
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=UserPublic, summary="Get a single user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# Endpoint C — Login (returns JWT access + refresh tokens)
# ---------------------------------------------------------------------------
@router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=200,
    summary="Login with email and password — returns JWT access and refresh tokens",
)
# Rate limited: max 10 login attempts per minute per IP
@limiter.limit("10/minute")
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    # Always return the same error for wrong email OR wrong password — never reveal which one failed
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# ---------------------------------------------------------------------------
# Endpoint D — Refresh (exchange refresh token for a new token pair)
# ---------------------------------------------------------------------------
@router.post(
    "/auth/refresh",
    response_model=TokenResponse,
    status_code=200,
    summary="Exchange a valid refresh token for a new access token",
)
def refresh(refresh_data: RefreshRequest):
    payload = decode_token(refresh_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_token_data = {"sub": payload["sub"], "role": payload["role"]}
    new_access = create_access_token(new_token_data)
    new_refresh = create_refresh_token(new_token_data)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


# ---------------------------------------------------------------------------
# Endpoint E — Get current user's profile
# ---------------------------------------------------------------------------
@router.get(
    "/auth/me",
    response_model=UserPublic,
    summary="Get the currently authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# Endpoint F — Logout
# ---------------------------------------------------------------------------
@router.post("/auth/logout", status_code=200)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint.
    JWT tokens are stateless — the server cannot invalidate them directly.
    The correct client-side logout pattern is:
1.	Delete the access_token and refresh_token from client storage
2.	Stop sending the Authorization header
    For production systems requiring server-side invalidation, implement
    a token blocklist using Redis. That is out of scope for this MVP.
    """
    return {
        "message": "Logged out successfully. Delete your tokens on the client side.",
        "user": current_user.email,
    }
