“””
VendBot - Система управления вендинговой сетью
Главная точка входа в приложение (Production Ready)
“””
import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH

sys.path.insert(0, str(Path(**file**).parent))

# Настройка базового логирования

logging.basicConfig(
level=logging.INFO,
format=’%(asctime)s - **%(name)s** - %(levelname)s - %(message)s’,
handlers=[
logging.StreamHandler(sys.stdout)
]
)

logger = logging.getLogger(“main”)

async def check_environment():
“”“Проверка переменных окружения”””
logger.info(“🔍 Checking environment variables…”)

```
# Проверяем обязательные переменные
required_vars = {
    'BOT_TOKEN': os.getenv('BOT_TOKEN'),
    'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development'),
    'DATABASE_URL': os.getenv('DATABASE_URL'),
    'REDIS_URL': os.getenv('REDIS_URL')
}

for var, value in required_vars.items():
    if value:
        if 'TOKEN' in var:
            logger.info(f"✅ {var}: {'*' * 20}...{value[-4:]}")
        else:
            logger.info(f"✅ {var}: {value}")
    else:
        logger.warning(f"⚠️ {var}: NOT SET")

return required_vars
```

async def init_app():
“”“Инициализация приложения”””
logger.info(“🚀 Starting VendBot v1.0.0”)

```
# Проверяем переменные окружения
env_vars = await check_environment()

logger.info(f"🔧 Environment: {env_vars['ENVIRONMENT']}")
logger.info(f"🐛 Debug mode: {os.getenv('DEBUG', 'False')}")

# Создаем необходимые директории
os.makedirs("logs", exist_ok=True)
os.makedirs("uploads/photos", exist_ok=True)
logger.info("📁 Required directories created")

return env_vars
```

async def start_telegram_bot(bot_token):
“”“Запуск Telegram бота”””
try:
logger.info(“🤖 Initializing Telegram Bot…”)

```
    # Простая проверка токена
    if not bot_token or len(bot_token.split(':')) != 2:
        raise ValueError("Invalid bot token format")
    
    # Попытка импорта aiogram
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        logger.info("✅ aiogram imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import aiogram: {e}")
        return False
    
    # Создаем бота
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Проверяем бота
    logger.info("🔗 Testing bot connection...")
    bot_info = await bot.get_me()
    logger.info(f"✅ Bot connected: @{bot_info.username} | {bot_info.first_name}")
    
    # Создаем диспетчер
    dp = Dispatcher()
    
    # Простой обработчик для теста
    @dp.message()
    async def echo_handler(message):
        await message.answer(
            f"🤖 <b>VendBot v1.0.0</b>\n\n"
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"✅ Бот работает в продакшене\n"
            f"📅 Время: {message.date}\n"
            f"🆔 Ваш ID: {message.from_user.id}\n\n"
            f"🔧 Система готова к работе!"
        )
    
    logger.info("📱 Starting bot polling...")
    await dp.start_polling(bot)
    
except Exception as e:
    logger.error(f"❌ Bot startup failed: {e}", exc_info=True)
    return False
```

async def demo_mode():
“”“Демо режим без бота”””
logger.info(“🤖 Starting demo mode…”)
logger.info(“📱 Bot interface will be implemented here”)
logger.info(“🔧 Currently in demo mode - missing bot token”)

```
# Короткий демо цикл
for i in range(3):
    await asyncio.sleep(10)
    logger.info(f"🔄 Demo heartbeat #{i+1} - System running")

logger.info("✅ Demo completed!")
```

async def main():
“”“Главная функция приложения”””
try:
# Инициализация
env_vars = await init_app()

```
    bot_token = env_vars.get('BOT_TOKEN')
    
    if bot_token and bot_token.strip():
        logger.info("🚀 Starting in BOT mode...")
        await start_telegram_bot(bot_token.strip())
    else:
        logger.warning("⚠️ BOT_TOKEN not found - starting demo mode")
        await demo_mode()
        
except KeyboardInterrupt:
    logger.info("🛑 Application stopped by user")
except Exception as e:
    logger.error(f"❌ Application error: {e}", exc_info=True)
    # В продакшене не падаем сразу
    if os.getenv('ENVIRONMENT') == 'production':
        logger.info("🔄 Restarting in 30 seconds...")
        await asyncio.sleep(30)
        await main()
    else:
        sys.exit(1)
finally:
    logger.info("🔚 VendBot shutdown complete")
```

if **name** == “**main**”:
# Проверяем Python версию
if sys.version_info < (3, 8):
print(“❌ Python 3.8+ required”)
sys.exit(1)

```
# Запускаем приложение
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n🛑 Application stopped")
except Exception as e:
    print(f"❌ Failed to start application: {e}")
    sys.exit(1)
```