"""
Pydantic schemas for user API endpoints.

Phase 3 — User schema definitions including authentication.
"""

from pydantic import BaseModel, Field, constr
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    analyst = "analyst"
    manager = "manager"
    field_technician = "field_technician"


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class UserCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=128)
    login_identifier: constr(min_length=1, max_length=128) = Field(..., description="Unique login identifier")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")
    role: UserRole = Field(default="analyst")
    account_status: UserStatus = Field(default="active")


class UserLogin(BaseModel):
    login_identifier: str
    password: str


class UserPublic(BaseModel):
    id: int
    display_name: str
    login_identifier: str
    email: Optional[str] = None
    role: str
    account_status: str
    preferences: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserPublic):
    password_hash: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=128)
    email: Optional[str] = Field(None, max_length=128)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    role: Optional[str] = None
    account_status: Optional[str] = None
    preferences: Optional[str] = None


class UserToken(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic
