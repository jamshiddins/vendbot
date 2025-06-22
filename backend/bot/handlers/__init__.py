"""
Регистрация всех обработчиков бота
"""
from aiogram import Dispatcher

# Импортируем все роутеры
from .common import router as common_router
from .warehouse import router as warehouse_router
from .operator import router as operator_router


def setup_all_handlers(dp: Dispatcher):
    """
    Регистрирует все обработчики в диспетчере
    
    Порядок регистрации важен! Более специфичные
    обработчики должны регистрироваться раньше общих.
    """
    # Сначала специфичные обработчики по ролям
    dp.include_router(warehouse_router)
    dp.include_router(operator_router)
    
    # В конце - общие обработчики и команды
    dp.include_router(common_router)


# Экспорт функции настройки
__all__ = ['setup_all_handlers']