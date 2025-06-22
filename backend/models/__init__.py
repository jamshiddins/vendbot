"""
Модели базы данных VendBot

Экспортирует все модели для удобного импорта:
from backend.models import User, Machine, Hopper
"""

# Базовые классы
from backend.models.base import Base, BaseModel, TimestampMixin

# Модели пользователей
from backend.models.user import (
    User, 
    UserRole, 
    UserRoleAssignment,
    user_roles_table
)

# Модели оборудования
from backend.models.equipment import (
    Machine,
    MachineStatus,
    Hopper,
    HopperStatus
)

# Модели склада
from backend.models.warehouse import (
    IngredientType,
    Inventory
)

# Модели операций
from backend.models.operations import (
    Operation,
    OperationType,
    Photo,
    PhotoType
)

# Импортируем модели транспорта (заглушки пока)
# from backend.models.transport import Vehicle, Trip

# Временные заглушки для транспорта
class Vehicle:
    pass

class Trip:
    pass

# Экспорт всех моделей
__all__ = [
    # Базовые
    'Base',
    'BaseModel', 
    'TimestampMixin',
    
    # Пользователи
    'User',
    'UserRole',
    'UserRoleAssignment',
    'user_roles_table',
    
    # Оборудование
    'Machine',
    'MachineStatus',
    'Hopper',
    'HopperStatus',
    
    # Склад
    'IngredientType',
    'Inventory',
    
    # Операции
    'Operation',
    'OperationType',
    'Photo',
    'PhotoType',
    
    # Транспорт
    'Vehicle',
    'Trip'
]

# Для проверки импортов
if __name__ == "__main__":
    print("✅ Все модели импортированы успешно!")
    print(f"Доступные модели: {', '.join(__all__)}")