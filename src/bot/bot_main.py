"""
VendBot Telegram Bot
"""
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import settings
from config.database import async_session_maker
from src.db.repositories.user import UserRepository
from src.db.models.user import UserRole

logger = logging.getLogger(__name__)

# Создаем бота и диспетчер
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    async with async_session_maker() as session:
        repo = UserRepository(session)
        db_user = await repo.get_by_telegram_id(user.id)
        
        if not db_user:
            # Новый пользователь - сохраняем в БД
            db_user = await repo.create(
                telegram_id=user.id,
                full_name=user.full_name,
                username=user.username
            )
            welcome_text = f"""
👋 Привет, {user.first_name}!

🤖 Я - VendBot, система управления вендинговой сетью.

📱 Вы зарегистрированы в системе.
⏸ Ожидайте назначения роли администратором.

Ваш ID: `{user.id}`
"""
        else:
            # Обновляем время последней активности
            db_user.last_active_at = datetime.utcnow()
            await repo.update(db_user)
            
            role_emoji = {
                UserRole.ADMIN: "👑",
                UserRole.WAREHOUSE: "🏭",
                UserRole.OPERATOR: "🔧",
                UserRole.DRIVER: "🚛"
            }
            
            welcome_text = f"""
👋 С возвращением, {user.first_name}!

🤖 VendBot - система управления вендинговой сетью.

{role_emoji.get(db_user.role, "📱")} Ваша роль: **{db_user.role.value}**
{"✅ Статус: Активен" if db_user.is_active else "❌ Статус: Заблокирован"}

Доступные команды:
/help - Справка по командам
/menu - Главное меню
/profile - Мой профиль
"""
    
    await message.answer(welcome_text, parse_mode="Markdown")
    logger.info(f"User {user.id} ({user.username}) started bot")


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Обработчик команды /profile"""
    user = message.from_user
    
    async with async_session_maker() as session:
        repo = UserRepository(session)
        db_user = await repo.get_by_telegram_id(user.id)
        
        if not db_user:
            await message.answer("❌ Вы не зарегистрированы в системе. Используйте /start")
            return
        
        role_names = {
            UserRole.ADMIN: "Администратор",
            UserRole.WAREHOUSE: "Склад",
            UserRole.OPERATOR: "Оператор",
            UserRole.DRIVER: "Водитель"
        }
        
        profile_text = f"""
👤 **Мой профиль**

🆔 ID: `{user.id}`
👤 Имя: {user.full_name}
📱 Username: @{user.username or "не указан"}
📞 Телефон: {db_user.phone or "не указан"}

🎭 Роль: {role_names.get(db_user.role, "Не назначена")}
📊 Статус: {"✅ Активен" if db_user.is_active else "❌ Заблокирован"}

📅 Регистрация: {db_user.created_at.strftime("%d.%m.%Y %H:%M")}
🕐 Последняя активность: {db_user.last_active_at.strftime("%d.%m.%Y %H:%M") if db_user.last_active_at else "Сейчас"}
"""
    
    await message.answer(profile_text, parse_mode="Markdown")


@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    """Управление пользователями (только для админов)"""
    async with async_session_maker() as session:
        repo = UserRepository(session)
        user = await repo.get_by_telegram_id(message.from_user.id)
        
        if not user or user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет доступа к этой команде")
            return
        
        # Получаем всех пользователей
        all_users = await repo.get_all_active()
        
        users_text = "👥 **Список пользователей:**\n\n"
        
        for u in all_users:
            role_emoji = {
                UserRole.ADMIN: "👑",
                UserRole.WAREHOUSE: "🏭", 
                UserRole.OPERATOR: "🔧",
                UserRole.DRIVER: "🚛"
            }
            
            users_text += f"{role_emoji.get(u.role, '📱')} {u.full_name} (@{u.username or 'нет'})\n"
            users_text += f"   ID: `{u.telegram_id}` | Роль: {u.role.value}\n\n"
        
        users_text += f"\n📊 Всего пользователей: {len(all_users)}"
        
        await message.answer(users_text, parse_mode="Markdown")


async def start_bot():
    """Запуск бота"""
    logger.info("Starting VendBot Telegram bot...")
    
    # Инициализируем БД
    from config.database import init_db
    await init_db()
    
    # Удаляем вебхуки если были
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling
    logger.info("Bot started successfully!")
    await dp.start_polling(bot)