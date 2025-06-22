"""
Модели для складского учета
"""
from typing import Optional
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.models.base import BaseModel


class IngredientType(BaseModel):
    """
    Типы ингредиентов
    
    Справочник всех видов ингредиентов,
    используемых в вендинговых автоматах.
    """
    __tablename__ = "ingredient_types"
    
    # Основные данные
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Название ингредиента"
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Категория (кофе, молоко, сиропы и т.д.)"
    )
    
    # Единицы измерения
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="кг",
        comment="Единица измерения (кг, л, шт)"
    )
    
    # Уровни запасов
    min_stock_level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=10.0,
        comment="Минимальный уровень запаса"
    )
    reorder_level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=20.0,
        comment="Уровень для заказа"
    )
    max_stock_level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
        comment="Максимальный уровень запаса"
    )
    
    # Дополнительно
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Описание ингредиента"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Активен ли ингредиент"
    )
    
    # Отношения
    inventory = relationship("Inventory", back_populates="ingredient_type", uselist=False)
    hoppers = relationship("Hopper", back_populates="ingredient_type")
    
    def __repr__(self) -> str:
        return f"<IngredientType(name={self.name}, category={self.category})>"
    
    @property
    def display_name(self) -> str:
        """Полное отображаемое имя"""
        return f"{self.category}: {self.name}"


class Inventory(BaseModel):
    """
    Складские остатки
    
    Отслеживает количество каждого ингредиента
    на складе с учетом резервирования.
    """
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint('ingredient_type_id', name='uq_inventory_ingredient'),
        CheckConstraint('quantity >= 0', name='ck_inventory_quantity_positive'),
        CheckConstraint('reserved_quantity >= 0', name='ck_inventory_reserved_positive'),
        CheckConstraint('reserved_quantity <= quantity', name='ck_inventory_reserved_not_exceed'),
    )
    
    # Ингредиент
    ingredient_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('ingredient_types.id'),
        nullable=False,
        unique=True,
        comment="ID типа ингредиента"
    )
    
    # Количества
    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Общее количество на складе"
    )
    reserved_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Зарезервированное количество"
    )
    
    # История
    last_restock_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последнего пополнения"
    )
    last_restock_quantity: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Количество последнего пополнения"
    )
    
    # Отношения
    ingredient_type = relationship("IngredientType", back_populates="inventory")
    
    def __repr__(self) -> str:
        return f"<Inventory(ingredient_id={self.ingredient_type_id}, qty={self.quantity})>"
    
    @property
    def available_quantity(self) -> float:
        """Доступное количество (не зарезервированное)"""
        return max(0, self.quantity - self.reserved_quantity)
    
    @property
    def stock_level_status(self) -> str:
        """Статус уровня запасов"""
        if not self.ingredient_type:
            return "unknown"
        
        if self.quantity <= self.ingredient_type.min_stock_level:
            return "critical"  # Критический
        elif self.quantity <= self.ingredient_type.reorder_level:
            return "low"       # Низкий
        elif self.quantity >= self.ingredient_type.max_stock_level:
            return "excess"    # Избыток
        else:
            return "normal"    # Нормальный
    
    @property
    def stock_level_emoji(self) -> str:
        """Эмодзи для уровня запасов"""
        status_emojis = {
            "critical": "🔴",
            "low": "🟡",
            "normal": "🟢",
            "excess": "🔵",
            "unknown": "⚪"
        }
        return status_emojis.get(self.stock_level_status, "⚪")
    
    def can_reserve(self, quantity: float) -> bool:
        """Проверка возможности резервирования"""
        return self.available_quantity >= quantity
    
    def reserve(self, quantity: float) -> bool:
        """Зарезервировать количество"""
        if self.can_reserve(quantity):
            self.reserved_quantity += quantity
            return True
        return False
    
    def release_reservation(self, quantity: float) -> bool:
        """Освободить резервирование"""
        if self.reserved_quantity >= quantity:
            self.reserved_quantity -= quantity
            return True
        return False
    
    def consume(self, quantity: float) -> bool:
        """Списать со склада"""
        if self.quantity >= quantity:
            self.quantity -= quantity
            # Уменьшаем резерв если он был
            if self.reserved_quantity > 0:
                self.reserved_quantity = max(0, self.reserved_quantity - quantity)
            return True
        return False
    
    def restock(self, quantity: float) -> None:
        """Пополнить склад"""
        self.quantity += quantity
        self.last_restock_date = datetime.now()
        self.last_restock_quantity = quantity


# Добавляем импорт Boolean для совместимости
from sqlalchemy import Boolean