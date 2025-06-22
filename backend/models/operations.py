"""
Модели для операций и фотофиксации
"""
from enum import Enum
from typing import Optional
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, BigInteger,
    ForeignKey, JSON, DateTime, Text
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.models.base import BaseModel


class OperationType(str, Enum):
    """Типы операций в системе"""
    # Пользователи
    USER_CREATED = "user_created"
    USER_BLOCKED = "user_blocked"
    USER_UNBLOCKED = "user_unblocked"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    
    # Склад
    INVENTORY_RECEIVE = "inventory_receive"
    INVENTORY_ISSUE = "inventory_issue"
    INVENTORY_ADJUST = "inventory_adjust"
    
    # Бункеры
    HOPPER_FILL = "hopper_fill"
    HOPPER_INSTALL = "hopper_install"
    HOPPER_REMOVE = "hopper_remove"
    HOPPER_CLEAN = "hopper_clean"
    ISSUE_HOPPER = "issue_hopper"
    RETURN_HOPPER = "return_hopper"
    
    # Автоматы
    MACHINE_SERVICE = "machine_service"
    MACHINE_REPAIR = "machine_repair"
    MACHINE_STATUS_CHANGE = "machine_status_change"
    
    # Транспорт
    START_TRIP = "start_trip"
    END_TRIP = "end_trip"
    FUEL_PURCHASE = "fuel_purchase"
    VEHICLE_SERVICE = "vehicle_service"
    
    # Отчеты
    PROBLEM_REPORT = "problem_report"
    INVENTORY_CHECK = "inventory_check"


class Operation(BaseModel):
    """
    Журнал операций
    
    Фиксирует все действия пользователей в системе
    для аудита и истории.
    """
    __tablename__ = "operations"
    
    # Основные данные
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=False,
        index=True,
        comment="ID пользователя, выполнившего операцию"
    )
    operation_type: Mapped[OperationType] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Тип операции"
    )
    
    # Целевой объект
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Тип объекта (user, hopper, machine и т.д.)"
    )
    entity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="ID объекта"
    )
    
    # Детали
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Описание операции"
    )
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Дополнительные данные операции"
    )
    
    # Статус
    success: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Успешность операции"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Сообщение об ошибке"
    )
    
    # Отношения
    user = relationship("User", back_populates="operations")
    photos = relationship("Photo", back_populates="operation", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Operation(id={self.id}, type={self.operation_type}, user_id={self.user_id})>"
    
    @property
    def display_type(self) -> str:
        """Отображаемое название операции"""
        type_names = {
            OperationType.USER_CREATED: "Создание пользователя",
            OperationType.USER_BLOCKED: "Блокировка пользователя",
            OperationType.USER_UNBLOCKED: "Разблокировка пользователя",
            OperationType.ROLE_ASSIGNED: "Назначение роли",
            OperationType.ROLE_REMOVED: "Снятие роли",
            OperationType.INVENTORY_RECEIVE: "Приёмка товара",
            OperationType.INVENTORY_ISSUE: "Выдача товара",
            OperationType.INVENTORY_ADJUST: "Корректировка остатков",
            OperationType.HOPPER_FILL: "Заполнение бункера",
            OperationType.HOPPER_INSTALL: "Установка бункера",
            OperationType.HOPPER_REMOVE: "Снятие бункера",
            OperationType.HOPPER_CLEAN: "Чистка бункера",
            OperationType.ISSUE_HOPPER: "Выдача бункера",
            OperationType.RETURN_HOPPER: "Возврат бункера",
            OperationType.MACHINE_SERVICE: "Обслуживание автомата",
            OperationType.MACHINE_REPAIR: "Ремонт автомата",
            OperationType.MACHINE_STATUS_CHANGE: "Смена статуса автомата",
            OperationType.START_TRIP: "Начало поездки",
            OperationType.END_TRIP: "Завершение поездки",
            OperationType.FUEL_PURCHASE: "Заправка",
            OperationType.VEHICLE_SERVICE: "ТО автомобиля",
            OperationType.PROBLEM_REPORT: "Отчет о проблеме",
            OperationType.INVENTORY_CHECK: "Инвентаризация"
        }
        return type_names.get(self.operation_type, self.operation_type)


class PhotoType(str, Enum):
    """Типы фотографий в системе"""
    HOPPER_INSTALL = "hopper_install"
    HOPPER_REMOVE = "hopper_remove"
    MACHINE_SERVICE = "machine_service"
    FUEL_RECEIPT = "fuel_receipt"
    VEHICLE_ODOMETER = "vehicle_odometer"
    PROBLEM_REPORT = "problem_report"
    INVENTORY_CHECK = "inventory_check"


class Photo(BaseModel):
    """
    Фотографии операций
    
    Хранит file_id от Telegram для быстрого доступа
    к фотографиям без необходимости их скачивания.
    """
    __tablename__ = "photos"
    
    # Связи
    operation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('operations.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID операции"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=False,
        comment="ID пользователя, загрузившего фото"
    )
    
    # Данные фотографии
    file_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Telegram file_id"
    )
    file_unique_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Telegram file_unique_id"
    )
    photo_type: Mapped[PhotoType] = mapped_column(
        String(50),
        nullable=False,
        comment="Тип фотографии"
    )
    
    # Дополнительная информация
    caption: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Подпись к фото"
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Размер файла в байтах"
    )
    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Ширина в пикселях"
    )
    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Высота в пикселях"
    )
    
    # Метаданные
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Дополнительные данные (GPS, параметры и т.д.)"
    )
    
    # Отношения
    operation = relationship("Operation", back_populates="photos")
    user = relationship("User", back_populates="photos")
    
    def __repr__(self) -> str:
        return f"<Photo(id={self.id}, type={self.photo_type}, operation_id={self.operation_id})>"
    
    @property
    def is_valid(self) -> bool:
        """Проверяет валидность фотографии"""
        return bool(self.file_id and self.file_unique_id)
    
    @property
    def telegram_file_id(self) -> str:
        """Возвращает file_id для использования в Telegram API"""
        return self.file_id
    
    @property
    def display_type(self) -> str:
        """Отображаемое название типа фото"""
        type_names = {
            PhotoType.HOPPER_INSTALL: "Установка бункера",
            PhotoType.HOPPER_REMOVE: "Снятие бункера",
            PhotoType.MACHINE_SERVICE: "Обслуживание автомата",
            PhotoType.FUEL_RECEIPT: "Чек заправки",
            PhotoType.VEHICLE_ODOMETER: "Показания одометра",
            PhotoType.PROBLEM_REPORT: "Фото проблемы",
            PhotoType.INVENTORY_CHECK: "Инвентаризация"
        }
        return type_names.get(self.photo_type, self.photo_type)


# Добавляем импорт Boolean
from sqlalchemy import Boolean