"""
User model
"""
from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    WAREHOUSE = "warehouse" 
    OPERATOR = "operator"
    DRIVER = "driver"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Telegram data
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Personal data
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Role and status
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.OPERATOR
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.full_name}, role={self.role.value})>"