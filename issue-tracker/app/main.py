from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

from app.database import engine, Base
import app.models as _models  # noqa: F401 — ensures Base.metadata discovers all models
from app.routers import users, projects, tickets

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Issue Tracker API",
    description="""
A lightweight issue tracking REST API.

## Resources
- **Users** — People who can be assigned to tickets
- **Projects** — Containers for tickets
- **Tickets** — Individual units of work with status, priority, and type

## Ticket Status Flow
`TODO` → `IN_PROGRESS` → `IN_REVIEW` → `DONE`
    """,
    version="1.0.0",
    contact={"name": "Engineering Team"},
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS middleware
# TODO: Replace localhost origins with real frontend domain before deploying
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------------------------------------------------------------------------
# HTTP security headers middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


# ---------------------------------------------------------------------------
# Startup event — create DB tables if they don't exist
# ---------------------------------------------------------------------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("  Database tables verified.")


# ---------------------------------------------------------------------------
# Global exception handler — catches any unhandled exception
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler. Logs the real error server-side but returns
    a generic message to the client so internal details are never leaked.
    """
    import traceback
    # Log full traceback to server console only — never send to client
    print(f"[ERROR] Unhandled exception on {request.method} {request.url}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# ---------------------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------------------
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tickets.router)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/", summary="Root — API status")
def root():
    return {
        "message": "Issue Tracker API is running",
        "docs": "/docs",
        "version": "1.0.0",
    }


# ---------------------------------------------------------------------------
# Health check endpoint
# ---------------------------------------------------------------------------
@app.get("/health", summary="Health check")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "database": "unreachable"},
        )
