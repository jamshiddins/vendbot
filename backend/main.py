"""
Главный файл приложения VendBot
Объединяет FastAPI сервер и Telegram бота
"""
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.core.database import init_db, close_db
from backend.bot.setup import start_polling, start_webhook, get_bot, get_dispatcher
from backend.api.main import router as api_router
from backend.api.reports import router as reports_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Получаем настройки
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    logger.info("Starting VendBot application...")
    
    # Выводим конфигурацию
    settings.print_config_summary()
    
    try:
        # Инициализация БД
        await init_db()
        logger.info("✅ Database initialized")
        
        # Запуск бота в зависимости от режима
        if settings.use_webhook:
            # Webhook режим - бот запустится через API endpoint
            logger.info("🌐 Bot configured for webhook mode")
            bot = get_bot()
            dp = get_dispatcher()
            
            # Устанавливаем webhook при старте
            await bot.set_webhook(
                url=f"{settings.webhook_url}/webhook/{settings.bot_token}",
                drop_pending_updates=True
            )
        else:
            # Polling режим - запускаем в фоне
            logger.info("🔄 Starting bot in polling mode...")
            asyncio.create_task(start_polling())
        
        logger.info("✅ VendBot is ready!")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    finally:
        # Очистка при завершении
        logger.info("Shutting down VendBot...")
        
        # Закрываем БД
        await close_db()
        
        # Останавливаем бота
        if not settings.use_webhook:
            bot = get_bot()
            await bot.session.close()
        
        logger.info("👋 VendBot stopped")


# Создаем приложение FastAPI
app = FastAPI(
    title="VendBot API",
    description="Система управления вендинговой сетью",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS (для будущего веб-интерфейса)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(api_router)
app.include_router(reports_router)

# Корневой endpoint
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "name": "VendBot",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.actual_deployment_stage,
        "features": {
            "api": "/api/v1",
            "docs": "/docs",
            "reports": "/api/v1/reports",
            "bot": {
                "mode": "webhook" if settings.use_webhook else "polling",
                "active": True
            }
        }
    }

# Health check для мониторинга
@app.get("/health")
async def health():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    }


if __name__ == "__main__":
    # Для локальной разработки
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )