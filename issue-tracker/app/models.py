from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
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
