"""
Модели оборудования: автоматы и бункеры
"""
from enum import Enum
from typing import Optional
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer, BigInteger,
    ForeignKey, DateTime, Boolean, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.models.base import BaseModel


class MachineStatus(str, Enum):
    """Статусы автоматов"""
    ACTIVE = "active"          # Работает
    MAINTENANCE = "maintenance" # На обслуживании
    BROKEN = "broken"          # Сломан
    INACTIVE = "inactive"      # Выключен


class Machine(BaseModel):
    """
    Модель вендингового автомата
    
    Хранит информацию о местоположении, состоянии
    и назначенном операторе.
    """
    __tablename__ = "machines"
    
    # Идентификация
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Уникальный код автомата"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Название/описание автомата"
    )
    
    # Местоположение
    location_address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Адрес установки"
    )
    location_details: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Детали местоположения (этаж, место)"
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Широта"
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Долгота"
    )
    
    # Состояние
    status: Mapped[MachineStatus] = mapped_column(
        String(20),
        nullable=False,
        default=MachineStatus.ACTIVE,
        comment="Текущий статус"
    )
    
    # Назначение
    assigned_operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
        comment="ID назначенного оператора"
    )
    
    # Даты
    installation_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата установки"
    )
    last_service_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последнего обслуживания"
    )
    
    # Дополнительно
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Дополнительные данные"
    )
    
    # Отношения
    assigned_operator = relationship("User", foreign_keys=[assigned_operator_id])
    hoppers = relationship("Hopper", back_populates="machine")
    
    def __repr__(self) -> str:
        return f"<Machine(code={self.code}, name={self.name}, status={self.status})>"
    
    @property
    def is_operational(self) -> bool:
        """Проверка работоспособности"""
        return self.status == MachineStatus.ACTIVE
    
    @property
    def display_location(self) -> str:
        """Отображаемый адрес"""
        if self.location_details:
            return f"{self.location_address}, {self.location_details}"
        return self.location_address


class HopperStatus(str, Enum):
    """Статусы бункеров"""
    EMPTY = "empty"        # Пустой
    FILLED = "filled"      # Заполнен
    INSTALLED = "installed" # Установлен на автомат
    CLEANING = "cleaning"  # На чистке/обслуживании


class Hopper(BaseModel):
    """
    Модель бункера для ингредиентов
    
    Отслеживает состояние, вес, содержимое
    и историю использования бункеров.
    """
    __tablename__ = "hoppers"
    
    # Идентификация
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Уникальный код бункера"
    )
    
    # Состояние
    status: Mapped[HopperStatus] = mapped_column(
        String(20),
        nullable=False,
        default=HopperStatus.EMPTY,
        index=True,
        comment="Текущий статус"
    )
    
    # Содержимое
    ingredient_type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('ingredient_types.id'),
        nullable=True,
        comment="ID типа ингредиента"
    )
    
    # Веса
    weight_empty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Вес пустого бункера (кг)"
    )
    weight_full: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Вес полного бункера (кг)"
    )
    current_weight: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Текущий вес (кг)"
    )
    
    # Назначения
    machine_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('machines.id'),
        nullable=True,
        comment="ID автомата"
    )
    assigned_operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
        comment="ID назначенного оператора"
    )
    
    # Даты
    last_filled_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последнего заполнения"
    )
    last_cleaned_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последней чистки"
    )
    
    # Отношения
    ingredient_type = relationship("IngredientType")
    machine = relationship("Machine", back_populates="hoppers")
    assigned_operator = relationship("User", foreign_keys=[assigned_operator_id])
    
    def __repr__(self) -> str:
        return f"<Hopper(code={self.code}, status={self.status})>"
    
    @property
    def ingredient_weight(self) -> float:
        """Вычисляет вес ингредиента"""
        if self.weight_full and self.weight_empty:
            return self.weight_full - self.weight_empty
        return 0.0
    
    @property
    def current_ingredient_weight(self) -> float:
        """Вычисляет текущий вес ингредиента"""
        if self.current_weight and self.weight_empty:
            return max(0, self.current_weight - self.weight_empty)
        return 0.0
    
    @property
    def fill_percentage(self) -> float:
        """Процент заполнения"""
        if self.ingredient_weight > 0:
            return (self.current_ingredient_weight / self.ingredient_weight) * 100
        return 0.0
    
    @property
    def needs_refill(self) -> bool:
        """Проверка необходимости пополнения"""
        return self.fill_percentage < 20  # Меньше 20%