"""
Настройка и инициализация Telegram бота
"""
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from backend.core.config import get_settings
from backend.core.database import get_async_session

logger = logging.getLogger(__name__)

# Глобальные объекты бота
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


def create_bot() -> Bot:
    """
    Создает экземпляр бота с настройками
    """
    settings = get_settings()
    
    # Настройки бота по умолчанию
    bot_properties = DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True,
        protect_content=False
    )
    
    # Создаем бота
    bot_instance = Bot(
        token=settings.bot_token,
        default=bot_properties
    )
    
    logger.info("✅ Telegram Bot создан")
    return bot_instance


def create_dispatcher() -> Dispatcher:
    """
    Создает диспетчер с настройками хранилища
    """
    settings = get_settings()
    
    # Выбираем хранилище состояний
    if settings.use_redis and settings.redis_url:
        storage = RedisStorage.from_url(settings.redis_url)
        logger.info("📦 Используется Redis для хранения состояний")
    else:
        storage = MemoryStorage()
        logger.info("💾 Используется Memory Storage для состояний")
    
    # Создаем диспетчер
    dispatcher = Dispatcher(storage=storage)
    
    # Добавляем middleware
    setup_middlewares(dispatcher)
    
    # Регистрируем обработчики
    setup_handlers(dispatcher)
    
    logger.info("✅ Dispatcher настроен")
    return dispatcher


def setup_middlewares(dispatcher: Dispatcher):
    """
    Настройка middleware для бота
    """
    from backend.bot.middleware.database import DatabaseMiddleware
    from backend.bot.middleware.auth import AuthMiddleware
    from backend.bot.middleware.logging import LoggingMiddleware
    
    # Порядок важен! Сначала логирование, потом БД, потом авторизация
    dispatcher.message.middleware(LoggingMiddleware())
    dispatcher.callback_query.middleware(LoggingMiddleware())
    
    dispatcher.message.middleware(DatabaseMiddleware())
    dispatcher.callback_query.middleware(DatabaseMiddleware())
    
    dispatcher.message.middleware(AuthMiddleware())
    dispatcher.callback_query.middleware(AuthMiddleware())
    
    logger.info("✅ Middleware подключены")


def setup_handlers(dispatcher: Dispatcher):
    """
    Регистрация всех обработчиков
    """
    from backend.bot.handlers import setup_all_handlers
    
    setup_all_handlers(dispatcher)
    logger.info("✅ Обработчики зарегистрированы")


async def on_startup(bot: Bot):
    """
    Действия при запуске бота
    """
    settings = get_settings()
    
    # Устанавливаем команды бота
    await setup_bot_commands(bot)
    
    # Настраиваем webhook если нужно
    if settings.use_webhook:
        await bot.set_webhook(
            url=settings.webhook_url,
            drop_pending_updates=True
        )
        logger.info(f"✅ Webhook установлен: {settings.webhook_url}")
    else:
        # Удаляем webhook если был
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook удален, используется polling")
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f"🤖 Бот запущен: @{bot_info.username}")


async def on_shutdown(bot: Bot):
    """
    Действия при остановке бота
    """
    # Закрываем сессию бота
    await bot.session.close()
    logger.info("👋 Бот остановлен")


async def setup_bot_commands(bot: Bot):
    """
    Устанавливает команды бота в меню
    """
    from aiogram.types import BotCommand
    
    commands = [
        BotCommand(command="start", description="🚀 Начать работу"),
        BotCommand(command="menu", description="📱 Главное меню"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="profile", description="👤 Мой профиль"),
        BotCommand(command="cancel", description="❌ Отменить операцию"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("✅ Команды бота установлены")


def get_bot() -> Bot:
    """
    Получить экземпляр бота
    """
    global bot
    if not bot:
        bot = create_bot()
    return bot


def get_dispatcher() -> Dispatcher:
    """
    Получить экземпляр диспетчера
    """
    global dp
    if not dp:
        dp = create_dispatcher()
    return dp


async def start_polling():
    """
    Запуск бота в режиме polling
    """
    bot = get_bot()
    dp = get_dispatcher()
    
    # Устанавливаем обработчики событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запускаем polling
    try:
        logger.info("🚀 Запуск бота в режиме polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


async def start_webhook(app: web.Application):
    """
    Запуск бота в режиме webhook
    """
    bot = get_bot()
    dp = get_dispatcher()
    settings = get_settings()
    
    # Устанавливаем обработчики событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Настраиваем webhook
    webhook_path = f"/webhook/{settings.bot_token}"
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=webhook_path)
    
    # Настраиваем приложение
    setup_application(app, dp, bot=bot)
    
    logger.info(f"🚀 Webhook настроен на пути: {webhook_path}")