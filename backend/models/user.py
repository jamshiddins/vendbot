"""
Модель пользователя и система ролей
"""
from enum import Enum
from typing import Optional, List, Set
from datetime import datetime

from sqlalchemy import (
    Column, String, BigInteger, Boolean, 
    Table, ForeignKey, DateTime, Integer
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.base import BaseModel, Base


class UserRole(str, Enum):
    """Роли пользователей в системе"""
    ADMIN = "admin"
    WAREHOUSE = "warehouse"
    OPERATOR = "operator"
    DRIVER = "driver"
    
    @classmethod
    def get_display_name(cls, role: str) -> str:
        """Получить отображаемое имя роли"""
        names = {
            cls.ADMIN: "Администратор",
            cls.WAREHOUSE: "Кладовщик",
            cls.OPERATOR: "Оператор",
            cls.DRIVER: "Водитель"
        }
        return names.get(role, role)


# Таблица связи пользователей и ролей (many-to-many)
user_roles_table = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', BigInteger, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role', String(50), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('assigned_by', BigInteger, ForeignKey('users.id'), nullable=True)
)


class User(BaseModel):
    """
    Модель пользователя
    
    Хранит информацию о пользователях системы,
    их роли и права доступа.
    """
    __tablename__ = "users"
    
    # Telegram данные
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, 
        unique=True, 
        nullable=False,
        index=True,
        comment="Telegram ID пользователя"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True,
        index=True,
        comment="Username в Telegram"
    )
    
    # Персональные данные
    full_name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="Полное имя пользователя"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="Номер телефона"
    )
    
    # Статус и разрешения
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        comment="Активен ли пользователь"
    )
    is_owner: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        comment="Является ли владельцем (суперадмин)"
    )
    
    # Отношения
    roles: Mapped[List["UserRoleAssignment"]] = relationship(
        "UserRoleAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="UserRoleAssignment.user_id"
    )
    
    # Обратные отношения для других моделей
    operations = relationship("Operation", back_populates="user")
    photos = relationship("Photo", back_populates="user")
    trips = relationship("Trip", back_populates="driver", foreign_keys="Trip.driver_id")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.full_name})>"
    
    # === Методы для работы с ролями ===
    
    @property
    def role_names(self) -> Set[str]:
        """Получить список названий ролей пользователя"""
        return {assignment.role for assignment in self.roles if assignment.is_active}
    
    def has_role(self, role: str) -> bool:
        """Проверить наличие роли"""
        if self.is_owner:  # Владелец имеет все права
            return True
        return role in self.role_names
    
    def has_any_role(self, *roles: str) -> bool:
        """Проверить наличие любой из указанных ролей"""
        if self.is_owner:
            return True
        user_roles = self.role_names
        return any(role in user_roles for role in roles)
    
    def is_admin(self) -> bool:
        """Проверить, является ли пользователь администратором"""
        return self.is_owner or self.has_role(UserRole.ADMIN)
    
    async def add_role(
        self, 
        role: str, 
        assigned_by_id: Optional[int] = None,
        session: AsyncSession = None
    ) -> bool:
        """Добавить роль пользователю"""
        # Проверяем, есть ли уже такая роль
        for assignment in self.roles:
            if assignment.role == role:
                if not assignment.is_active:
                    # Активируем существующую роль
                    assignment.is_active = True
                    assignment.assigned_at = datetime.now()
                    assignment.assigned_by_id = assigned_by_id
                    return True
                return False  # Роль уже активна
        
        # Создаем новое назначение
        new_assignment = UserRoleAssignment(
            user_id=self.id,
            role=role,
            assigned_by_id=assigned_by_id
        )
        self.roles.append(new_assignment)
        
        if session:
            session.add(new_assignment)
        
        return True
    
    async def remove_role(self, role: str) -> bool:
        """Удалить роль у пользователя"""
        for assignment in self.roles:
            if assignment.role == role and assignment.is_active:
                assignment.is_active = False
                assignment.removed_at = datetime.now()
                return True
        return False
    
    def get_display_roles(self) -> str:
        """Получить строку с ролями для отображения"""
        if self.is_owner:
            return "👑 Владелец"
        
        role_emojis = {
            UserRole.ADMIN: "👨‍💼",
            UserRole.WAREHOUSE: "📦", 
            UserRole.OPERATOR: "🔧",
            UserRole.DRIVER: "🚚"
        }
        
        roles = []
        for role_name in sorted(self.role_names):
            emoji = role_emojis.get(role_name, "👤")
            display_name = UserRole.get_display_name(role_name)
            roles.append(f"{emoji} {display_name}")
        
        return ", ".join(roles) if roles else "👤 Без роли"


class UserRoleAssignment(BaseModel):
    """
    Назначение роли пользователю с историей
    """
    __tablename__ = "user_role_assignments"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    # Кто назначил
    assigned_by_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Активность роли
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    removed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Отношения
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    
    def __repr__(self) -> str:
        return f"<UserRoleAssignment(user_id={self.user_id}, role={self.role}, active={self.is_active})>"


# Для обратной совместимости и импорта
from sqlalchemy import func