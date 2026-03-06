import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# In production (Render), DATABASE_URL is set automatically when you attach a PostgreSQL database.
# Locally it falls back to SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./issue_tracker.db")

# Render's PostgreSQL URL starts with "postgres://" — SQLAlchemy requires "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False. PostgreSQL does not accept that arg.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
