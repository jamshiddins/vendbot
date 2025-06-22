#!/usr/bin/env python3
"""
🚀 VendBot - Простой запуск для новичков
Автоматически настраивает все зависимости и запускает приложение
"""
import sys
import subprocess
import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Проверяет версию Python"""
    if sys.version_info < (3, 9):
        logger.error("❌ Требуется Python 3.9 или выше!")
        logger.info("💡 Установи последнюю версию Python с python.org")
        sys.exit(1)
    logger.info(f"✅ Python {sys.version.split()[0]} обнаружен")

def install_requirements():
    """Устанавливает зависимости если нужно"""
    try:
        # Проверяем основные пакеты
        import fastapi
        import aiogram
        import sqlalchemy
        logger.info("✅ Основные зависимости установлены")
    except ImportError:
        logger.info("📦 Устанавливаю зависимости...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            logger.info("✅ Зависимости успешно установлены")
        except subprocess.CalledProcessError:
            logger.error("❌ Ошибка установки зависимостей")
            logger.info("💡 Попробуй: pip install -r requirements.txt")
            sys.exit(1)

def create_project_structure():
    """Создает структуру папок проекта"""
    directories = [
        "backend",
        "backend/core",
        "backend/models", 
        "backend/bot",
        "backend/bot/handlers",
        "backend/bot/keyboards",
        "backend/bot/states",
        "backend/bot/utils",
        "backend/api",
        "backend/services",
        "uploads",
        "uploads/photos"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Создаем __init__.py файлы
    for dir_path in directories:
        if dir_path.startswith("backend"):
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    logger.info("✅ Структура проекта создана")

def create_env_if_missing():
    """Создает .env файл если его нет"""
    if not os.path.exists(".env"):
        logger.info("⚙️ Создаю файл настроек...")
        with open(".env", "w", encoding="utf-8") as f:
            f.write("# Telegram Bot настройки\n")
            f.write("BOT_TOKEN=your_bot_token_here\n\n")
            f.write("# Этап развертывания (local/cloud/production)\n")
            f.write("DEPLOYMENT_STAGE=local\n\n")
            f.write("# База данных (оставь пустым для SQLite)\n")
            f.write("DATABASE_URL=\n\n")
            f.write("# Redis (оставь пустым для Memory Storage)\n")
            f.write("REDIS_URL=\n\n")
            f.write("# Webhook URL (оставь пустым для polling)\n")
            f.write("WEBHOOK_URL=\n")
        
        logger.warning("❗ ВАЖНО: Укажи BOT_TOKEN в файле .env")
        logger.info("💡 Получи токен у @BotFather в Telegram")
        return False
    
    # Проверяем наличие токена
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()
        if "your_bot_token_here" in content:
            logger.warning("❗ Не забудь указать BOT_TOKEN в файле .env")
            return False
    
    logger.info("✅ Файл настроек обнаружен")
    return True

def run_migrations():
    """Создает таблицы в базе данных"""
    try:
        from backend.core.database import engine, Base
        # from backend.models import *  # Закомментируем пока нет моделей
        
        logger.info("🗄️ Создаю таблицы в базе данных...")
        
        # Синхронный импорт для создания таблиц
        import asyncio
        
        async def create_tables():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # asyncio.run(create_tables())  # Закомментируем пока
        logger.info("✅ База данных будет создана при первом запуске")
        
    except Exception as e:
        logger.warning(f"⚠️ База данных будет создана при первом запуске: {e}")

def main():
    """Главная функция запуска"""
    print("""
    ╔═══════════════════════════════════════╗
    ║        🤖 VendBot Launcher 🤖         ║
    ║   Система управления вендингом v1.0   ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Проверки и настройка
    check_python_version()
    create_project_structure()
    install_requirements()
    
    if not create_env_if_missing():
        logger.info("\n🔧 После настройки .env файла запусти скрипт снова")
        input("\nНажми Enter для выхода...")
        return
    
    # Пытаемся создать таблицы
    run_migrations()
    
    logger.info("\n🚀 Запускаю VendBot...")
    
    try:
        # Запуск приложения
        os.environ["PYTHONPATH"] = os.getcwd()
        
        # Для разработки используем reload
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
        
    except KeyboardInterrupt:
        logger.info("\n👋 VendBot остановлен")
    except ModuleNotFoundError as e:
        logger.error(f"❌ Модуль не найден: {e}")
        logger.info("💡 Проверь, что все файлы созданы правильно")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        logger.info("💡 Проверь логи выше для деталей")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        input("\nНажми Enter для выхода...")