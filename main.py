"""
VendBot - Система управления вендинговой сетью
Главная точка входа в приложение
"""

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска приложения"""
    
    try:
        # Импортируем настройки после загрузки .env
        from config.settings import settings
        
        logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
        logger.info(f"🔧 Environment: {settings.environment}")
        logger.info(f"🐛 Debug mode: {settings.debug}")
        
        # Создание необходимых папок
        Path("logs").mkdir(exist_ok=True)
        Path("uploads/photos").mkdir(parents=True, exist_ok=True)
        
        logger.info("📁 Required directories created")
        
        # Проверяем токен бота
        if settings.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.warning("⚠️ Bot token not set! Please configure BOT_TOKEN in .env file")
            logger.info("📝 Running in demo mode...")
            
            # Демо-режим без реального бота
            logger.info("🤖 Starting demo mode...")
            logger.info("📱 Bot interface will be implemented here")
            logger.info("🔧 Currently in development mode")
            
            # Простой цикл для демонстрации работы
            counter = 0
            while True:
                await asyncio.sleep(5)
                counter += 1
                logger.info(f"🔄 Demo heartbeat #{counter} - System running normally")
                
                if counter >= 6:  # Остановка после 30 секунд для демо
                    logger.info("✅ Demo completed successfully!")
                    break
        else:
            logger.info("🔑 Bot token found, starting real bot...")
            
            try:
                # Попытка импорта и запуска бота
                from src.bot.main import create_bot, start_polling
                
                bot = await create_bot()
                logger.info("🤖 Bot created successfully")
                
                await start_polling(bot)
                
            except ImportError as e:
                logger.warning(f"📦 Bot modules not ready: {e}")
                logger.info("🔧 Running in basic mode with real token...")
                
                # Простая проверка токена
                try:
                    from aiogram import Bot
                    bot = Bot(token=settings.BOT_TOKEN)
                    me = await bot.get_me()
                    logger.info(f"✅ Bot connected: {me.first_name} (@{me.username})")
                    await bot.session.close()
                    
                    logger.info("🎯 Bot is ready for development!")
                    logger.info("📚 Next steps:")
                    logger.info("   1. Implement bot handlers")
                    logger.info("   2. Set up database")
                    logger.info("   3. Create user roles")
                    
                except Exception as bot_error:
                    logger.error(f"❌ Bot connection failed: {bot_error}")
                    logger.info("🔧 Please check your bot token")
                
            except Exception as e:
                logger.error(f"❌ Bot startup error: {e}")
                logger.info("🔧 Running in demo mode...")
                
    except KeyboardInterrupt:
        logger.info("⏹️ Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        logger.error(f"📍 Error details: {type(e).__name__}: {str(e)}")
        raise
    finally:
        logger.info("🔚 VendBot shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())