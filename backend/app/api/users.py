"""
FastAPI routers for user identity endpoints.

Phase 3 — User authentication and profile API routes.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserPublic, UserUpdate, UserToken
from app.services.users_service import AuthService
from app.repositories.users import UserRepository
from app.models import User
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_active_user


router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = AuthService.get_by_login_identifier(db, user_data.login_identifier)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login identifier already registered",
        )
    user = AuthService.create_user(db, user_data.dict())
    return UserPublic.from_orm(user)


@router.post("/login", response_model=UserToken)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return an access token."""
    user = AuthService.authenticate(db, credentials.login_identifier, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role, "account_status": user.account_status}
    )
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "user": UserPublic.from_orm(user),
    }


@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Get the current authenticated user."""
    return UserPublic.from_orm(current_user)


@router.put("/me", response_model=UserPublic)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user profile, role, email, and preferences."""
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = AuthService.get_password_hash(update_data.pop("password"))
    updated = UserRepository.update(db, current_user, update_data)
    return UserPublic.from_orm(updated)


@router.get("/", response_model=List[UserPublic])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_active_user),
):
    """List all users (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    users = UserRepository.get_all(db, skip, limit)
    return [UserPublic.from_orm(u) for u in users]


@router.get("/{user_id}", response_model=UserPublic)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: UserPublic = Depends(get_current_active_user)):
    """Get a user by ID."""
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.role != "admin" and user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return UserPublic.from_orm(user)


@router.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_active_user),
):
    """Update a user (admin or self)."""
    if current_user.role != "admin" and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_user = UserRepository.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = AuthService.get_password_hash(update_data.pop("password"))
    updated = UserRepository.update(db, db_user, update_data)
    return UserPublic.from_orm(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserPublic = Depends(get_current_active_user)):
    """Delete a user (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    db_user = UserRepository.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete own account")
    UserRepository.delete(db, db_user)
    return None
