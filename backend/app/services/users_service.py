"""
Business logic and orchestration layer for user operations.

Phase 3 — User service with password hashing and authentication.
"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.models import User
from app.repositories.users import UserRepository
from app.core.config import get_settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes


class AuthService:
    """Service layer for user authentication and authorization."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def get_by_login_identifier(db: Session, login_identifier: str) -> Optional[User]:
        """Retrieve a user by login identifier."""
        return UserRepository.get_by_login_identifier(db, login_identifier)

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """Create a new user with a hashed password."""
        password_hash = AuthService.get_password_hash(user_data["password"])
        user_data = {k: v for k, v in user_data.items() if k != "password"}
        user_data["password_hash"] = password_hash
        user = User(**user_data)
        return UserRepository.create(db, user)

    @staticmethod
    def authenticate(db: Session, login_identifier: str, password: str) -> Optional[User]:
        """Authenticate a user by login identifier and password."""
        user = UserRepository.get_by_login_identifier(db, login_identifier)
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        if user.account_status != "active":
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
