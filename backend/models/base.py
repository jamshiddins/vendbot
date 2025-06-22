"""
Базовые классы и миксины для моделей
"""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class TimestampMixin:
    """
    Миксин для автоматических временных меток
    Добавляет created_at и updated_at во все модели
    """
    
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            comment="Время создания записи"
        )
    
    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
            comment="Время последнего обновления"
        )


class BaseModel(Base, TimestampMixin):
    """
    Базовая модель с ID и временными метками
    Наследуйте от неё для автоматического добавления полей
    """
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор"
    )
    
    def __repr__(self) -> str:
        """Строковое представление объекта"""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict[str, Any]:
        """Преобразование в словарь"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseModel":
        """Создание объекта из словаря"""
        return cls(**data)


# Экспорт
__all__ = ["Base", "BaseModel", "TimestampMixin"]