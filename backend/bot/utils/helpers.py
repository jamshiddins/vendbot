"""
Вспомогательные функции для бота
"""
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from aiogram import types
from aiogram.utils.markdown import hcode, hbold, hitalic, hlink


def escape_html(text: str) -> str:
    """
    Экранирует HTML символы в тексте
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def format_phone(phone: str) -> str:
    """
    Форматирует номер телефона
    
    Args:
        phone: Номер телефона
        
    Returns:
        Отформатированный номер
    """
    # Удаляем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    
    # Форматируем
    if len(digits) == 11 and digits.startswith('7'):
        # Российский формат
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    elif len(digits) == 10:
        # Без кода страны
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    else:
        # Возвращаем как есть
        return phone


def format_datetime(dt: datetime, format: str = "full") -> str:
    """
    Форматирует дату и время
    
    Args:
        dt: Объект datetime
        format: Формат (full, date, time, short)
        
    Returns:
        Отформатированная строка
    """
    if not dt:
        return "—"
    
    formats = {
        "full": "%d.%m.%Y %H:%M",
        "date": "%d.%m.%Y",
        "time": "%H:%M",
        "short": "%d.%m %H:%M"
    }
    
    return dt.strftime(formats.get(format, formats["full"]))


def format_timedelta(td: timedelta) -> str:
    """
    Форматирует временной интервал
    
    Args:
        td: Объект timedelta
        
    Returns:
        Человекочитаемая строка
    """
    total_seconds = int(td.total_seconds())
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    
    parts = []
    
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0:
        parts.append(f"{minutes} мин.")
    
    return " ".join(parts) if parts else "менее минуты"


def format_number(number: float, decimals: int = 2) -> str:
    """
    Форматирует число с разделителями разрядов
    
    Args:
        number: Число
        decimals: Количество знаков после запятой
        
    Returns:
        Отформатированная строка
    """
    if decimals > 0:
        formatted = f"{number:,.{decimals}f}"
    else:
        formatted = f"{int(number):,}"
    
    # Заменяем запятые на пробелы (русский формат)
    return formatted.replace(",", " ").replace(".", ",")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Обрезает текст до указанной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста
        
    Returns:
        Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_phone(phone: str) -> bool:
    """
    Проверяет валидность номера телефона
    
    Args:
        phone: Номер телефона
        
    Returns:
        True если валидный
    """
    # Удаляем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    
    # Проверяем длину
    return len(digits) in [10, 11]


def parse_callback_data(callback_data: str) -> Dict[str, str]:
    """
    Парсит callback_data в словарь
    
    Args:
        callback_data: Строка callback_data
        
    Returns:
        Словарь с данными
    
    Example:
        "admin:user:view:123" -> {
            "module": "admin",
            "entity": "user",
            "action": "view",
            "id": "123"
        }
    """
    parts = callback_data.split(":")
    
    result = {}
    
    if len(parts) >= 1:
        result["module"] = parts[0]
    if len(parts) >= 2:
        result["entity"] = parts[1]
    if len(parts) >= 3:
        result["action"] = parts[2]
    if len(parts) >= 4:
        result["id"] = parts[3]
    
    # Дополнительные параметры
    for i, part in enumerate(parts[4:], 4):
        result[f"param{i-3}"] = part
    
    return result


def get_user_mention(user: types.User) -> str:
    """
    Создает упоминание пользователя
    
    Args:
        user: Объект пользователя Telegram
        
    Returns:
        HTML ссылка на пользователя
    """
    name = escape_html(user.full_name)
    return hlink(name, f"tg://user?id={user.id}")


def split_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Разбивает список на части
    
    Args:
        lst: Исходный список
        chunk_size: Размер части
        
    Returns:
        Список списков
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def calculate_percentage(current: float, total: float) -> float:
    """
    Вычисляет процент
    
    Args:
        current: Текущее значение
        total: Общее значение
        
    Returns:
        Процент (0-100)
    """
    if total == 0:
        return 0
    
    return min(100, max(0, (current / total) * 100))


def get_progress_bar(
    current: float,
    total: float,
    length: int = 10,
    filled: str = "▓",
    empty: str = "░"
) -> str:
    """
    Создает прогресс-бар
    
    Args:
        current: Текущее значение
        total: Общее значение
        length: Длина бара
        filled: Символ заполнения
        empty: Символ пустоты
        
    Returns:
        Строка прогресс-бара
    """
    percentage = calculate_percentage(current, total)
    filled_length = int(length * percentage / 100)
    
    bar = filled * filled_length + empty * (length - filled_length)
    
    return f"{bar} {percentage:.0f}%"


def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла
    
    Args:
        size_bytes: Размер в байтах
        
    Returns:
        Человекочитаемый размер
    """
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} ТБ"


def is_valid_telegram_id(telegram_id: str) -> bool:
    """
    Проверяет валидность Telegram ID
    
    Args:
        telegram_id: ID для проверки
        
    Returns:
        True если валидный
    """
    try:
        tid = int(telegram_id)
        return tid > 0
    except (ValueError, TypeError):
        return False


def create_mention_list(users: List[Any], separator: str = ", ") -> str:
    """
    Создает список упоминаний пользователей
    
    Args:
        users: Список пользователей (должны иметь telegram_id и full_name)
        separator: Разделитель
        
    Returns:
        Строка с упоминаниями
    """
    mentions = []
    
    for user in users:
        name = escape_html(user.full_name)
        mention = hlink(name, f"tg://user?id={user.telegram_id}")
        mentions.append(mention)
    
    return separator.join(mentions)


# Константы для сообщений
MAX_MESSAGE_LENGTH = 4096
MAX_CAPTION_LENGTH = 1024
MAX_CALLBACK_DATA_LENGTH = 64

# Эмодзи для разных статусов
STATUS_EMOJIS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "loading": "⏳",
    "done": "✨",
    "new": "🆕",
    "hot": "🔥",
    "locked": "🔒",
    "unlocked": "🔓",
}


# Экспорт функций
__all__ = [
    # Форматирование
    'escape_html',
    'format_phone',
    'format_datetime',
    'format_timedelta',
    'format_number',
    'truncate_text',
    'format_file_size',
    
    # Валидация
    'validate_phone',
    'is_valid_telegram_id',
    
    # Утилиты
    'parse_callback_data',
    'get_user_mention',
    'split_list',
    'calculate_percentage',
    'get_progress_bar',
    'create_mention_list',
    
    # Константы
    'MAX_MESSAGE_LENGTH',
    'MAX_CAPTION_LENGTH',
    'MAX_CALLBACK_DATA_LENGTH',
    'STATUS_EMOJIS',
]