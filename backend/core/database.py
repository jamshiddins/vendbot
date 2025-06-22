"""
Конфигурация базы данных для VendBot
Поддерживает SQLite для разработки и PostgreSQL для production
"""
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from backend.core.config import get_settings

logger = logging.getLogger(__name__)

# Получаем настройки
settings = get_settings()

# База для всех моделей
Base = declarative_base()

# Создаем асинхронный движок
engine = create_async_engine(
    settings.actual_database_url,
    echo=settings.log_level == "DEBUG",
    future=True,
    # Для SQLite используем NullPool
    poolclass=NullPool if "sqlite" in settings.actual_database_url else None,
    # Настройки пула для PostgreSQL
    pool_size=20 if "postgresql" in settings.actual_database_url else None,
    max_overflow=0 if "postgresql" in settings.actual_database_url else None,
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД
    
    Usage:
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_async_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Инициализация базы данных
    Создает все таблицы если их нет
    """
    try:
        logger.info("Инициализация базы данных...")
        
        # Импортируем все модели чтобы они зарегистрировались
        from backend.models import (
            User, Machine, Hopper, 
            IngredientType, Inventory,
            Operation, Photo,
            Vehicle, Trip
        )
        
        async with engine.begin() as conn:
            # Создаем таблицы
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ База данных инициализирована")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise


async def close_db():
    """
    Закрытие соединений с БД
    """
    await engine.dispose()
    logger.info("База данных закрыта")


# Экспорт для использования в моделях
__all__ = [
    "Base",
    "engine", 
    "async_session_maker",
    "get_async_session",
    "init_db",
    "close_db"
]