from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    # Never store or log plain-text passwords
    hashed_password = Column(String, nullable=False, default="")
    # Allowed values: "admin" or "member"
    # The first user created becomes admin — this is handled at the application layer
    role = Column(String, nullable=False, default="member")
    created_at = Column(
        String, nullable=False, default=lambda: datetime.utcnow().isoformat()
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        String, nullable=False, default=lambda: datetime.utcnow().isoformat()
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="TODO")
    priority = Column(String, nullable=False, default="MEDIUM")
    type = Column(String, nullable=False, default="TASK")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        String, nullable=False, default=lambda: datetime.utcnow().isoformat()
    )
    updated_at = Column(
        String, nullable=False, default=lambda: datetime.utcnow().isoformat()
    )
