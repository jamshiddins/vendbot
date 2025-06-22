"""
Общие обработчики команд для всех ролей
"""
import logging

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.user import User, UserRole
from backend.bot.keyboards.menus import (
    get_main_menu, get_phone_keyboard, remove_keyboard
)
from backend.bot.states.all_states import CommonStates
from backend.bot.utils.helpers import escape_html, format_phone
from backend.bot.utils.decorators import with_error_handling, log_action

logger = logging.getLogger(__name__)
router = Router(name="common")


@router.message(CommandStart())
@with_error_handling
async def cmd_start(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext
):
    """Обработчик команды /start"""
    # Очищаем состояние
    await state.clear()
    
    telegram_id = message.from_user.id
    
    # Проверяем, существует ли пользователь
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        # Пользователь существует
        if not user.is_active:
            await message.answer(
                "❌ Ваш аккаунт заблокирован.\n"
                "Обратитесь к администратору для разблокировки."
            )
            return
        
        # Обновляем username если изменился
        if message.from_user.username != user.username:
            user.username = message.from_user.username
            await session.commit()
        
        # Приветствуем существующего пользователя
        text = f"""
👋 Добро пожаловать, {escape_html(user.full_name)}!

Ваши роли: {user.get_display_roles()}

Выберите действие из меню:
"""
        await message.answer(
            text,
            reply_markup=get_main_menu(list(user.role_names))
        )
        
    else:
        # Новый пользователь - начинаем регистрацию
        text = f"""
👋 Добро пожаловать в VendBot!

Я помогу вам управлять вендинговой сетью.

Для начала работы необходимо зарегистрироваться.

Как вас зовут? Введите ваше полное имя:
"""
        await message.answer(text, reply_markup=remove_keyboard())
        await state.set_state(CommonStates.registration_name)


@router.message(CommonStates.registration_name)
@with_error_handling
async def process_registration_name(
    message: types.Message,
    state: FSMContext
):
    """Обработка ввода имени при регистрации"""
    full_name = message.text.strip()
    
    # Валидация имени
    if len(full_name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите полное имя:")
        return
    
    if len(full_name) > 100:
        await message.answer("❌ Имя слишком длинное. Максимум 100 символов:")
        return
    
    # Сохраняем имя
    await state.update_data(full_name=full_name)
    
    # Запрашиваем телефон
    text = f"""
✅ Отлично, {escape_html(full_name)}!

Теперь отправьте ваш номер телефона для связи.

Нажмите кнопку ниже или введите номер вручную:
"""
    await message.answer(text, reply_markup=get_phone_keyboard())
    await state.set_state(CommonStates.registration_phone)


@router.message(CommonStates.registration_phone)
@with_error_handling
async def process_registration_phone(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    """Обработка номера телефона при регистрации"""
    phone = None
    
    # Если отправлен контакт
    if message.contact:
        phone = message.contact.phone_number
    # Если введен вручную
    elif message.text:
        phone = message.text.strip()
    
    if not phone:
        await message.answer(
            "❌ Отправьте номер телефона",
            reply_markup=get_phone_keyboard()
        )
        return
    
    # Форматируем номер
    formatted_phone = format_phone(phone)
    
    # Получаем данные из состояния
    data = await state.get_data()
    full_name = data['full_name']
    
    # Создаем пользователя
    new_user = User(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=full_name,
        phone=formatted_phone,
        is_active=True
    )
    
    session.add(new_user)
    await session.commit()
    
    # Очищаем состояние
    await state.clear()
    
    # Приветствуем нового пользователя
    text = f"""
✅ Регистрация завершена!

Ваши данные:
👤 Имя: {escape_html(full_name)}
📱 Телефон: {formatted_phone}

Для получения ролей обратитесь к администратору.

Ваш Telegram ID: `{message.from_user.id}`
(нажмите чтобы скопировать)
"""
    
    await message.answer(
        text,
        reply_markup=get_main_menu([]),
        parse_mode="Markdown"
    )
    
    logger.info(f"New user registered: {new_user.telegram_id} - {new_user.full_name}")


@router.message(Command("menu"))
@with_error_handling
@log_action("open_menu")
async def cmd_menu(
    message: types.Message,
    user: User,
    state: FSMContext
):
    """Обработчик команды /menu"""
    # Очищаем состояние
    await state.clear()
    
    text = f"""
📱 <b>Главное меню</b>

Пользователь: {escape_html(user.full_name)}
Роли: {user.get_display_roles()}

Выберите действие:
"""
    
    await message.answer(
        text,
        reply_markup=get_main_menu(list(user.role_names))
    )


@router.message(Command("help"))
@with_error_handling
async def cmd_help(message: types.Message, user: User):
    """Обработчик команды /help"""
    text = """
❓ <b>Помощь по работе с ботом</b>

<b>Основные команды:</b>
/start - Начать работу
/menu - Главное меню
/help - Эта справка
/profile - Ваш профиль
/cancel - Отменить текущую операцию

<b>Навигация:</b>
- Используйте кнопки под сообщениями
- Кнопка "🔙 Назад" вернет к предыдущему меню
- Кнопка "❌ Отмена" отменит текущую операцию

<b>По ролям:</b>
"""
    
    if user.has_role(UserRole.ADMIN):
        text += """
👨‍💼 <b>Администратор:</b>
- Управление пользователями
- Просмотр статистики
- Генерация отчетов
"""
    
    if user.has_role(UserRole.WAREHOUSE):
        text += """
📦 <b>Склад:</b>
- Приёмка товаров
- Выдача бункеров
- Инвентаризация
"""
    
    if user.has_role(UserRole.OPERATOR):
        text += """
🔧 <b>Оператор:</b>
- Установка/снятие бункеров
- Обслуживание автоматов
- Отчеты о проблемах
"""
    
    if user.has_role(UserRole.DRIVER):
        text += """
🚚 <b>Водитель:</b>
- Начало/завершение поездок
- Отметки о заправках
- Путевые листы
"""
    
    text += """

<b>Поддержка:</b>
Если у вас есть вопросы, обратитесь к администратору.
"""
    
    await message.answer(text)


@router.message(Command("profile"))
@with_error_handling
@log_action("view_profile")
async def cmd_profile(message: types.Message, user: User):
    """Обработчик команды /profile"""
    from backend.bot.utils.helpers import format_datetime
    
    text = f"""
👤 <b>Ваш профиль</b>

🆔 ID: <code>{user.telegram_id}</code>
👤 Имя: {escape_html(user.full_name)}
📱 Телефон: {user.phone or 'Не указан'}
🔗 Username: @{user.username or 'не указан'}

📋 Роли: {user.get_display_roles()}
📊 Статус: {'✅ Активен' if user.is_active else '❌ Заблокирован'}

📅 Регистрация: {format_datetime(user.created_at)}
🔄 Обновлено: {format_datetime(user.updated_at)}
"""
    
    await message.answer(text)


@router.message(Command("cancel"))
@with_error_handling
async def cmd_cancel(
    message: types.Message,
    state: FSMContext,
    user: User
):
    """Обработчик команды /cancel"""
    current_state = await state.get_state()
    
    if current_state:
        await state.clear()
        await message.answer(
            "❌ Операция отменена",
            reply_markup=remove_keyboard()
        )
        
        # Показываем главное меню
        await cmd_menu(message, user, state)
    else:
        await message.answer("Нечего отменять")


@router.callback_query(F.data == "back_to_menu")
@with_error_handling
async def callback_back_to_menu(
    callback: types.CallbackQuery,
    user: User,
    state: FSMContext
):
    """Возврат в главное меню"""
    # Очищаем состояние
    await state.clear()
    
    text = f"""
📱 <b>Главное меню</b>

Пользователь: {escape_html(user.full_name)}
Роли: {user.get_display_roles()}

Выберите действие:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu(list(user.role_names))
    )
    await callback.answer()


@router.callback_query(F.data == "profile")
@with_error_handling
@log_action("view_profile_inline")
async def callback_profile(callback: types.CallbackQuery, user: User):
    """Просмотр профиля через inline кнопку"""
    from backend.bot.utils.helpers import format_datetime
    from backend.bot.keyboards.menus import get_back_button
    
    text = f"""
👤 <b>Ваш профиль</b>

🆔 ID: <code>{user.telegram_id}</code>
👤 Имя: {escape_html(user.full_name)}
📱 Телефон: {user.phone or 'Не указан'}
🔗 Username: @{user.username or 'не указан'}

📋 Роли: {user.get_display_roles()}
📊 Статус: {'✅ Активен' if user.is_active else '❌ Заблокирован'}

📅 Регистрация: {format_datetime(user.created_at)}
🔄 Обновлено: {format_datetime(user.updated_at)}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "help")
@with_error_handling
async def callback_help(callback: types.CallbackQuery, user: User):
    """Справка через inline кнопку"""
    from backend.bot.keyboards.menus import get_back_button
    
    text = """
❓ <b>Помощь по работе с ботом</b>

<b>Основные команды:</b>
/start - Начать работу
/menu - Главное меню
/help - Эта справка
/profile - Ваш профиль
/cancel - Отменить текущую операцию

<b>Навигация:</b>
- Используйте кнопки под сообщениями
- Кнопка "🔙 Назад" вернет к предыдущему меню
- Кнопка "❌ Отмена" отменит текущую операцию
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "back")
@with_error_handling
async def callback_back(
    callback: types.CallbackQuery,
    user: User,
    state: FSMContext
):
    """Универсальная кнопка назад"""
    # Здесь можно добавить логику возврата к предыдущему состоянию
    # Пока просто возвращаем в главное меню
    await callback_back_to_menu(callback, user, state)


@router.callback_query(F.data == "cancel")
@with_error_handling
async def callback_cancel(
    callback: types.CallbackQuery,
    user: User,
    state: FSMContext
):
    """Универсальная кнопка отмены"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Операция отменена",
        reply_markup=get_main_menu(list(user.role_names))
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: types.CallbackQuery):
    """Заглушка для неактивных кнопок"""
    await callback.answer()


# Обработчик неизвестных сообщений
@router.message()
@with_error_handling
async def unknown_message(message: types.Message, user: User, state: FSMContext):
    """Обработчик неизвестных сообщений"""
    current_state = await state.get_state()
    
    if current_state:
        # Если есть активное состояние - не мешаем
        return
    
    await message.answer(
        "❓ Не понимаю эту команду.\n"
        "Используйте /menu для открытия главного меню."
    )


# Экспорт роутера
__all__ = ['router']