"""
Декораторы для обработчиков бота
"""
import logging
from functools import wraps
from typing import Callable, Union, List

from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User, UserRole

logger = logging.getLogger(__name__)


def role_required(*roles: str):
    """
    Декоратор для проверки ролей пользователя
    
    Usage:
        @role_required("admin", "warehouse")
        async def handler(message: types.Message, user: User, ...):
            pass
    """
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(
            event: Union[types.Message, types.CallbackQuery],
            user: User,
            *args,
            **kwargs
        ):
            # Проверяем наличие хотя бы одной из требуемых ролей
            if not user.has_any_role(*roles):
                error_text = "❌ У вас недостаточно прав для выполнения этой операции"
                
                if isinstance(event, types.CallbackQuery):
                    await event.answer(error_text, show_alert=True)
                else:
                    await event.answer(error_text)
                
                logger.warning(
                    f"Access denied for user {user.telegram_id} "
                    f"(roles: {user.role_names}) to {handler.__name__}"
                )
                return
            
            # Вызываем оригинальный обработчик
            return await handler(event, user, *args, **kwargs)
        
        return wrapper
    return decorator


def admin_only(handler: Callable):
    """
    Декоратор для функций только для администраторов
    
    Usage:
        @admin_only
        async def handler(message: types.Message, user: User, ...):
            pass
    """
    return role_required(UserRole.ADMIN)(handler)


def owner_only(handler: Callable):
    """
    Декоратор для функций только для владельца
    
    Usage:
        @owner_only
        async def handler(message: types.Message, user: User, ...):
            pass
    """
    @wraps(handler)
    async def wrapper(
        event: Union[types.Message, types.CallbackQuery],
        user: User,
        *args,
        **kwargs
    ):
        if not user.is_owner:
            error_text = "❌ Эта функция доступна только владельцу системы"
            
            if isinstance(event, types.CallbackQuery):
                await event.answer(error_text, show_alert=True)
            else:
                await event.answer(error_text)
            
            logger.warning(f"Owner access denied for user {user.telegram_id}")
            return
        
        return await handler(event, user, *args, **kwargs)
    
    return wrapper


def with_error_handling(handler: Callable):
    """
    Декоратор для обработки ошибок
    
    Usage:
        @with_error_handling
        async def handler(message: types.Message, ...):
            pass
    """
    @wraps(handler)
    async def wrapper(*args, **kwargs):
        try:
            return await handler(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {handler.__name__}: {e}", exc_info=True)
            
            # Ищем объект для ответа пользователю
            event = None
            for arg in args:
                if isinstance(arg, (types.Message, types.CallbackQuery)):
                    event = arg
                    break
            
            if event:
                error_text = (
                    "❌ Произошла ошибка при выполнении операции.\n"
                    "Попробуйте позже или обратитесь к администратору."
                )
                
                if isinstance(event, types.CallbackQuery):
                    await event.answer(error_text, show_alert=True)
                else:
                    await event.answer(error_text)
    
    return wrapper


def log_action(action_type: str):
    """
    Декоратор для логирования действий пользователя
    
    Usage:
        @log_action("view_profile")
        async def handler(message: types.Message, user: User, ...):
            pass
    """
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(
            event: Union[types.Message, types.CallbackQuery],
            user: User,
            *args,
            **kwargs
        ):
            # Логируем действие
            logger.info(
                f"Action: {action_type} | "
                f"User: {user.telegram_id} ({user.full_name}) | "
                f"Handler: {handler.__name__}"
            )
            
            # Вызываем обработчик
            result = await handler(event, user, *args, **kwargs)
            
            # Можно добавить сохранение в БД если нужно
            # session = kwargs.get('session')
            # if session:
            #     operation = Operation(
            #         user_id=user.id,
            #         operation_type=action_type,
            #         ...
            #     )
            #     session.add(operation)
            
            return result
        
        return wrapper
    return decorator


def active_user_only(handler: Callable):
    """
    Декоратор для проверки активности пользователя
    
    Usage:
        @active_user_only
        async def handler(message: types.Message, user: User, ...):
            pass
    """
    @wraps(handler)
    async def wrapper(
        event: Union[types.Message, types.CallbackQuery],
        user: User,
        *args,
        **kwargs
    ):
        if not user.is_active:
            error_text = (
                "❌ Ваш аккаунт заблокирован.\n"
                "Обратитесь к администратору для разблокировки."
            )
            
            if isinstance(event, types.CallbackQuery):
                await event.answer(error_text, show_alert=True)
            else:
                await event.answer(error_text)
            
            logger.warning(f"Blocked user {user.telegram_id} tried to access {handler.__name__}")
            return
        
        return await handler(event, user, *args, **kwargs)
    
    return wrapper


def rate_limit(max_calls: int = 5, period: int = 60):
    """
    Декоратор для ограничения частоты вызовов
    
    Args:
        max_calls: Максимальное количество вызовов
        period: Период в секундах
    
    Usage:
        @rate_limit(max_calls=3, period=60)
        async def handler(message: types.Message, ...):
            pass
    """
    # Простая реализация через словарь в памяти
    # В production лучше использовать Redis
    call_history = {}
    
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(
            event: Union[types.Message, types.CallbackQuery],
            *args,
            **kwargs
        ):
            from datetime import datetime, timedelta
            
            # Получаем ID пользователя
            user_id = event.from_user.id
            now = datetime.now()
            
            # Очищаем старые записи
            if user_id in call_history:
                call_history[user_id] = [
                    timestamp for timestamp in call_history[user_id]
                    if now - timestamp < timedelta(seconds=period)
                ]
            else:
                call_history[user_id] = []
            
            # Проверяем лимит
            if len(call_history[user_id]) >= max_calls:
                error_text = f"⏱ Слишком много запросов. Подождите {period} секунд."
                
                if isinstance(event, types.CallbackQuery):
                    await event.answer(error_text, show_alert=True)
                else:
                    await event.answer(error_text)
                
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return
            
            # Добавляем текущий вызов
            call_history[user_id].append(now)
            
            # Вызываем обработчик
            return await handler(event, *args, **kwargs)
        
        return wrapper
    return decorator


# Экспорт декораторов
__all__ = [
    'role_required',
    'admin_only',
    'owner_only',
    'with_error_handling',
    'log_action',
    'active_user_only',
    'rate_limit'
]