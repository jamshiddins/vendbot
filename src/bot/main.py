"""Простой VendBot - основной модуль (aiogram 3.2.0 совместимый)"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, BotCommand
from aiogram.filters import Command

logger = logging.getLogger(__name__)


async def create_bot() -> Bot:
    """Создание экземпляра бота"""
    
    # Получаем токен из настроек
    from config.settings import settings
    
    if not settings.bot_token or settings.bot_token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Bot token not configured!")
        raise ValueError("Bot token not configured")
    
    # Для aiogram 3.2.0 - упрощенное создание бота
    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    
    logger.info("✅ Bot instance created successfully")
    return bot


# Простые команды бота
async def cmd_start(message: Message):
    """Команда /start"""
    user = message.from_user
    
    logger.info(f"👤 User {user.username} ({user.id}) started bot")
    
    text = f"""
🤖 <b>Добро пожаловать в VendBot!</b>

👋 Привет, {user.full_name}!

🎯 <b>VendBot</b> - система управления вендинговой сетью

📋 <b>Доступные команды:</b>
/start - Главное меню  
/help - Справка по системе
/status - Статус системы
/profile - Мой профиль

📞 <b>Поддержка:</b> Обратитесь к администратору

<i>VendBot v1.0.0 - Enterprise Vending Management</i>
    """
    
    await message.answer(text)


async def cmd_help(message: Message):
    """Команда /help"""
    text = """
📋 <b>Справка VendBot</b>

🤖 <b>О системе:</b>
VendBot - комплексная система управления вендинговой сетью

🎯 <b>Основные функции:</b>
• Учет вендинговых машин
• Управление бункерами и ингредиентами  
• Контроль остатков на складе
• Фотофиксация всех операций
• Маршрутизация и логистика
• Отчетность и аналитика

👥 <b>Роли пользователей:</b>
👑 Администратор - полное управление системой
🏭 Склад - управление запасами и поставками
🔧 Оператор - обслуживание автоматов
🚛 Водитель - логистика и перевозки

📞 <b>Поддержка:</b>
Обратитесь к администратору для получения доступа
    """
    await message.answer(text)


async def cmd_status(message: Message):
    """Команда /status"""
    
    from datetime import datetime
    
    text = f"""
📊 <b>Статус системы VendBot</b>

🤖 <b>Бот:</b> Активен ✅
🗄️ <b>База данных:</b> В разработке 🔧
📊 <b>Версия:</b> v1.0.0
🌍 <b>Окружение:</b> Development

⏰ <b>Время сервера:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

🔄 <b>Режим работы:</b> Разработка  
📈 <b>Статус:</b> Готов к использованию
    """
    await message.answer(text)


async def cmd_profile(message: Message):
    """Команда /profile"""
    user = message.from_user
    
    text = f"""
👤 <b>Профиль пользователя</b>

🆔 <b>ID:</b> {user.id}
👤 <b>Имя:</b> {user.full_name}
📝 <b>Username:</b> @{user.username or 'не указан'}
🎭 <b>Роль:</b> Не назначена
📊 <b>Статус:</b> Неавторизован

⚠️ <b>Доступ:</b>
Для получения доступа к системе обратитесь к администратору.

📞 <b>Контакты поддержки:</b>
Администратор системы VendBot
    """
    await message.answer(text)


async def create_dispatcher() -> Dispatcher:
    """Создание диспетчера"""
    dp = Dispatcher()
    
    # Регистрация команд
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_profile, Command("profile"))
    
    logger.info("✅ Bot handlers registered")
    return dp


async def setup_bot_commands(bot: Bot):
    """Настройка команд бота"""
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="help", description="❓ Справка по системе"),
        BotCommand(command="status", description="📊 Статус системы"),
        BotCommand(command="profile", description="👤 Мой профиль"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("✅ Bot commands configured")


async def start_polling(bot: Bot):
    """Запуск поллинга бота"""
    dp = await create_dispatcher()
    
    try:
        # Информация о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Bot started: @{bot_info.username}")
        logger.info(f"📱 Bot name: {bot_info.first_name}")
        
        # Удаление webhook и настройка команд
        await bot.delete_webhook(drop_pending_updates=True)
        await setup_bot_commands(bot)
        
        logger.info("🚀 VendBot is ready to serve!")
        logger.info("📨 Send /start to begin interaction")
        logger.info("━" * 50)
        
        # Запуск поллинга
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Bot polling error: {e}")
        raise
    finally:
        await bot.session.close()