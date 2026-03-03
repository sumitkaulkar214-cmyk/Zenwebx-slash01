from pydantic import BaseModel, ConfigDict
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: str

class UserRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Project Schemas
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Ticket Schemas
class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    type: str = "TASK"
    assignee_id: Optional[int] = None

class TicketUpdate(BaseModel):
    "All fields are optional to support partial PATCH updates."
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    type: Optional[str] = None
    assignee_id: Optional[int] = None

class TicketRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    type: str
    status: str
    project_id: int
    assignee_id: Optional[int] = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
