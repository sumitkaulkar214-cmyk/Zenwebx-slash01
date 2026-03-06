from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional


# User Schemas
class UserRegister(BaseModel):
    """Schema for public self-registration. Role is always set to 'member' by the server."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=100)


class UserCreate(BaseModel):
    """Schema for admin-created users. Allows role to be set explicitly."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field("member", pattern="^(admin|member)$")


class UserPublic(BaseModel):
    """Safe response schema — deliberately excludes hashed_password."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    created_at: str


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Project Schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Ticket Schemas
class TicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: str = Field("MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    type: str = Field("TASK", pattern="^(BUG|FEATURE|TASK|IMPROVEMENT)$")
    assignee_id: Optional[int] = Field(None, gt=0, description="Must be a positive integer user ID")


class TicketUpdate(BaseModel):
    """All fields are optional to support partial PATCH updates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, pattern="^(TODO|IN_PROGRESS|IN_REVIEW|DONE)$")
    priority: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    type: Optional[str] = Field(None, pattern="^(BUG|FEATURE|TASK|IMPROVEMENT)$")
    assignee_id: Optional[int] = Field(None, gt=0)


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


# Auth / Token Schemas
class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
