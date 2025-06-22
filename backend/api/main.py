"""
Основные API роуты для VendBot
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from aiogram import types

from backend.core.database import get_async_session
from backend.core.config import get_settings
from backend.bot.setup import get_bot, get_dispatcher
from backend.models import User, Machine, Hopper, Inventory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["api"])

# Настройки
settings = get_settings()


@router.get("/", response_model=Dict[str, Any])
async def api_root():
    """
    Корневой endpoint API
    """
    return {
        "name": "VendBot API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "stats": "/api/v1/stats",
            "webhook": f"/webhook/{settings.bot_token}"
        }
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка здоровья приложения
    """
    try:
        # Проверяем подключение к БД
        result = await session.execute(select(func.count(User.id)))
        user_count = result.scalar()
        
        return {
            "status": "healthy",
            "database": "connected",
            "users": user_count,
            "bot_token_set": bool(settings.bot_token),
            "environment": settings.actual_deployment_stage
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/stats", response_model=Dict[str, Any])
async def get_stats(session: AsyncSession = Depends(get_async_session)):
    """
    Получение общей статистики системы
    """
    try:
        # Статистика пользователей
        total_users = await session.scalar(
            select(func.count(User.id))
        )
        active_users = await session.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        )
        
        # Статистика оборудования
        total_machines = await session.scalar(
            select(func.count(Machine.id))
        )
        active_machines = await session.scalar(
            select(func.count(Machine.id)).where(Machine.status == "active")
        )
        
        # Статистика бункеров
        total_hoppers = await session.scalar(
            select(func.count(Hopper.id))
        )
        filled_hoppers = await session.scalar(
            select(func.count(Hopper.id)).where(Hopper.status == "filled")
        )
        installed_hoppers = await session.scalar(
            select(func.count(Hopper.id)).where(Hopper.status == "installed")
        )
        
        # Статистика склада
        ingredient_types = await session.scalar(
            select(func.count(Inventory.id))
        )
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "blocked": total_users - active_users
            },
            "machines": {
                "total": total_machines,
                "active": active_machines,
                "inactive": total_machines - active_machines
            },
            "hoppers": {
                "total": total_hoppers,
                "filled": filled_hoppers,
                "installed": installed_hoppers,
                "empty": total_hoppers - filled_hoppers - installed_hoppers
            },
            "warehouse": {
                "ingredient_types": ingredient_types
            }
        }
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Webhook endpoint для Telegram
@router.post(f"/webhook/{settings.bot_token}")
async def telegram_webhook(request: Request):
    """
    Обработка webhook от Telegram
    """
    try:
        bot = get_bot()
        dp = get_dispatcher()
        
        # Получаем данные
        data = await request.json()
        
        # Создаем объект Update
        update = types.Update(**data)
        
        # Обрабатываем через диспетчер
        await dp.feed_webhook_update(bot, update)
        
        return {"ok": True}
    
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return {"ok": False, "error": str(e)}


@router.get("/test-db")
async def test_database(session: AsyncSession = Depends(get_async_session)):
    """
    Тестовый endpoint для проверки работы с БД
    """
    try:
        # Простой запрос
        result = await session.execute(select(1))
        value = result.scalar()
        
        # Проверяем таблицы
        tables_query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
        """
        
        if "postgresql" in settings.actual_database_url:
            tables_query = """
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
            """
        
        result = await session.execute(tables_query)
        tables = [row[0] for row in result.fetchall()]
        
        return {
            "status": "connected",
            "database_url": settings.actual_database_url.split("@")[-1] if "@" in settings.actual_database_url else "local",
            "tables": tables,
            "tables_count": len(tables)
        }
    
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Экспорт роутера
__all__ = ['router']