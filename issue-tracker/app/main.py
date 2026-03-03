from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import engine, Base
import app.models  # ensures Base.metadata discovers all models
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
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
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
