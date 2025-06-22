"""
Клавиатуры и меню для всех ролей
"""
from typing import List, Optional

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from backend.models.user import UserRole


# ===== ГЛАВНЫЕ МЕНЮ ДЛЯ РОЛЕЙ =====

def get_main_menu(user_roles: List[str]) -> InlineKeyboardMarkup:
    """
    Создает главное меню в зависимости от ролей пользователя
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки для всех
    builder.row(
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="help")
    )
    
    # Кнопки по ролям
    if UserRole.ADMIN in user_roles:
        builder.row(
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")
        )
    
    if UserRole.WAREHOUSE in user_roles:
        builder.row(
            InlineKeyboardButton(text="📦 Склад", callback_data="warehouse:menu")
        )
    
    if UserRole.OPERATOR in user_roles:
        builder.row(
            InlineKeyboardButton(text="🔧 Задания", callback_data="operator:tasks")
        )
    
    if UserRole.DRIVER in user_roles:
        builder.row(
            InlineKeyboardButton(text="🚚 Поездки", callback_data="driver:trips")
        )
    
    # Настройки
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    
    return builder.as_markup()


def get_admin_menu() -> InlineKeyboardMarkup:
    """Меню администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="admin:search_user"),
        InlineKeyboardButton(text="📋 Списки пользователей", callback_data="admin:user_lists")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
        InlineKeyboardButton(text="📑 Отчеты", callback_data="admin:reports")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


def get_warehouse_menu() -> InlineKeyboardMarkup:
    """Меню склада"""
    builder = InlineKeyboardBuilder()
    
    # Основные операции
    builder.row(
        InlineKeyboardButton(text="📥 Приёмка", callback_data="warehouse:receive"),
        InlineKeyboardButton(text="📤 Выдача", callback_data="warehouse:issue")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Заполнение", callback_data="warehouse:fill"),
        InlineKeyboardButton(text="↩️ Возврат", callback_data="warehouse:return")
    )
    
    # Просмотр и отчеты
    builder.row(
        InlineKeyboardButton(text="📊 Остатки", callback_data="warehouse:stock"),
        InlineKeyboardButton(text="📜 История", callback_data="warehouse:history")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Инвентаризация", callback_data="warehouse:inventory")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


def get_operator_menu() -> InlineKeyboardMarkup:
    """Меню оператора"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📦 Установить бункер", callback_data="operator:install"),
        InlineKeyboardButton(text="📤 Снять бункер", callback_data="operator:remove")
    )
    builder.row(
        InlineKeyboardButton(text="🔧 Обслуживание", callback_data="operator:service"),
        InlineKeyboardButton(text="⚠️ Сообщить о проблеме", callback_data="operator:report")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои автоматы", callback_data="operator:machines"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="operator:stats")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


def get_driver_menu() -> InlineKeyboardMarkup:
    """Меню водителя"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🚗 Начать поездку", callback_data="driver:start_trip"),
        InlineKeyboardButton(text="🏁 Завершить поездку", callback_data="driver:end_trip")
    )
    builder.row(
        InlineKeyboardButton(text="⛽ Заправка", callback_data="driver:fuel"),
        InlineKeyboardButton(text="📍 Маршрут", callback_data="driver:route")
    )
    builder.row(
        InlineKeyboardButton(text="📋 История поездок", callback_data="driver:history"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="driver:stats")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


# ===== ОБЩИЕ КЛАВИАТУРЫ =====

def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 Назад", callback_data="back")
    ]])


def get_cancel_button() -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    ]])


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    )
    return builder.as_markup()


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура Да/Нет"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data="yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data="no")
    )
    return builder.as_markup()


# ===== СПЕЦИАЛЬНЫЕ КЛАВИАТУРЫ =====

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отправки номера телефона"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text="📱 Отправить номер телефона",
        request_contact=True
    ))
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отправки локации"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text="📍 Отправить местоположение",
        request_location=True
    ))
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def remove_keyboard() -> ReplyKeyboardRemove:
    """Удаление Reply клавиатуры"""
    return ReplyKeyboardRemove()


# ===== ПАГИНАЦИЯ =====

def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str
) -> InlineKeyboardMarkup:
    """
    Клавиатура пагинации
    
    Args:
        current_page: Текущая страница (начиная с 1)
        total_pages: Всего страниц
        callback_prefix: Префикс для callback_data
    """
    builder = InlineKeyboardBuilder()
    
    buttons = []
    
    # Кнопка "В начало"
    if current_page > 2:
        buttons.append(InlineKeyboardButton(
            text="⏮", 
            callback_data=f"{callback_prefix}:page:1"
        ))
    
    # Кнопка "Назад"
    if current_page > 1:
        buttons.append(InlineKeyboardButton(
            text="◀️",
            callback_data=f"{callback_prefix}:page:{current_page-1}"
        ))
    
    # Текущая страница
    buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data="noop"
    ))
    
    # Кнопка "Вперед"
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton(
            text="▶️",
            callback_data=f"{callback_prefix}:page:{current_page+1}"
        ))
    
    # Кнопка "В конец"
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton(
            text="⏭",
            callback_data=f"{callback_prefix}:page:{total_pages}"
        ))
    
    builder.row(*buttons)
    
    return builder.as_markup()


# ===== ДИНАМИЧЕСКИЕ КЛАВИАТУРЫ =====

def create_selection_keyboard(
    items: List[tuple],  # [(text, callback_data), ...]
    columns: int = 2,
    back_callback: str = "back"
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру выбора из списка элементов
    
    Args:
        items: Список кортежей (текст, callback_data)
        columns: Количество столбцов
        back_callback: Callback для кнопки "Назад"
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем элементы
    for text, callback_data in items:
        builder.button(text=text, callback_data=callback_data)
    
    # Организуем в строки
    builder.adjust(columns)
    
    # Добавляем кнопку назад
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback))
    
    return builder.as_markup()


# Экспорт
__all__ = [
    # Главные меню
    'get_main_menu',
    'get_admin_menu',
    'get_warehouse_menu',
    'get_operator_menu',
    'get_driver_menu',
    
    # Общие кнопки
    'get_back_button',
    'get_cancel_button',
    'get_confirm_keyboard',
    'get_yes_no_keyboard',
    
    # Специальные
    'get_phone_keyboard',
    'get_location_keyboard',
    'remove_keyboard',
    
    # Утилиты
    'get_pagination_keyboard',
    'create_selection_keyboard'
]