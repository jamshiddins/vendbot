"""
Обработчики для роли Склад
"""
import logging
from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.models.user import User
from backend.models.warehouse import IngredientType, Inventory
from backend.models.hopper import Hopper, HopperStatus
from backend.bot.keyboards.menus import (
    get_warehouse_menu, get_back_button, get_cancel_button
)
from backend.bot.utils.decorators import role_required, with_error_handling
from backend.bot.utils.helpers import escape_html, format_number, get_progress_bar

logger = logging.getLogger(__name__)
router = Router(name="warehouse")


@router.callback_query(F.data == "warehouse:menu")
@with_error_handling
@role_required("warehouse", "admin")
async def warehouse_menu(callback: types.CallbackQuery, user: User, session: AsyncSession):
    """Главное меню склада"""
    # Получаем статистику
    
    # Количество типов ингредиентов
    total_types = await session.scalar(
        select(func.count(IngredientType.id))
    )
    
    # Количество с низким запасом
    low_stock = await session.scalar(
        select(func.count(Inventory.id))
        .join(IngredientType)
        .where(Inventory.quantity <= IngredientType.min_stock_level)
    )
    
    # Количество пустых бункеров
    empty_hoppers = await session.scalar(
        select(func.count(Hopper.id))
        .where(Hopper.status == HopperStatus.EMPTY)
    )
    
    # Количество заполненных бункеров
    filled_hoppers = await session.scalar(
        select(func.count(Hopper.id))
        .where(Hopper.status == HopperStatus.FILLED)
    )
    
    text = f"""
📦 <b>Склад</b>

Сотрудник: {escape_html(user.full_name)}

<b>📊 Статистика:</b>
- Типов ингредиентов: {total_types}
- Низкий запас: {low_stock} {'⚠️' if low_stock > 0 else '✅'}
- Пустых бункеров: {empty_hoppers}
- Заполненных бункеров: {filled_hoppers}

Выберите действие:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_warehouse_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "warehouse:stock")
@with_error_handling
@role_required("warehouse", "admin")
async def view_stock(callback: types.CallbackQuery, session: AsyncSession):
    """Просмотр остатков на складе"""
    # Получаем все ингредиенты с остатками
    stmt = select(IngredientType, Inventory).join(
        Inventory, 
        IngredientType.id == Inventory.ingredient_type_id,
        isouter=True
    ).order_by(IngredientType.category, IngredientType.name)
    
    result = await session.execute(stmt)
    ingredients = result.all()
    
    if not ingredients:
        await callback.answer("На складе пусто", show_alert=True)
        return
    
    text = "📊 <b>Остатки на складе</b>\n\n"
    
    current_category = None
    for ingredient_type, inventory in ingredients:
        # Заголовок категории
        if ingredient_type.category != current_category:
            current_category = ingredient_type.category
            text += f"\n<b>{current_category.upper()}</b>\n"
        
        # Данные по ингредиенту
        quantity = inventory.quantity if inventory else 0
        reserved = inventory.reserved_quantity if inventory else 0
        available = quantity - reserved
        
        # Определяем статус
        if inventory:
            emoji = inventory.stock_level_emoji
        else:
            emoji = "🔴"
        
        # Прогресс-бар
        progress = get_progress_bar(
            quantity,
            ingredient_type.max_stock_level,
            length=8
        )
        
        text += (
            f"{emoji} <b>{ingredient_type.name}</b>\n"
            f"   {progress}\n"
            f"   Всего: {format_number(quantity, 1)} {ingredient_type.unit} | "
            f"Доступно: {format_number(available, 1)} {ingredient_type.unit}\n"
        )
        
        # Предупреждения
        if quantity <= ingredient_type.min_stock_level:
            text += f"   ⚠️ <i>Требуется пополнение!</i>\n"
        elif quantity <= ingredient_type.reorder_level:
            text += f"   📦 <i>Рекомендуется заказать</i>\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "warehouse:receive")
@with_error_handling
@role_required("warehouse", "admin")
async def start_receive(callback: types.CallbackQuery):
    """Начало процесса приёмки товара"""
    # Заглушка - полная реализация в отдельном файле
    text = """
📥 <b>Приёмка товара</b>

Функция приёмки товара позволяет:
- Выбрать тип ингредиента
- Указать количество
- Автоматически обновить остатки

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "warehouse:issue")
@with_error_handling
@role_required("warehouse", "admin")
async def start_issue(callback: types.CallbackQuery):
    """Начало процесса выдачи бункеров"""
    text = """
📤 <b>Выдача бункеров</b>

Функция выдачи позволяет:
- Выбрать заполненные бункеры
- Назначить их оператору
- Отследить передачу

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "warehouse:fill")
@with_error_handling
@role_required("warehouse", "admin")
async def start_fill(callback: types.CallbackQuery):
    """Начало процесса заполнения бункера"""
    text = """
🔄 <b>Заполнение бункеров</b>

Функция заполнения позволяет:
- Выбрать пустой бункер
- Выбрать ингредиент
- Взвесить и заполнить
- Автоматически списать со склада

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "warehouse:return")
@with_error_handling
@role_required("warehouse", "admin")
async def start_return(callback: types.CallbackQuery):
    """Начало процесса возврата бункера"""
    text = """
↩️ <b>Возврат бункеров</b>

Функция возврата позволяет:
- Принять бункер от оператора
- Взвесить остатки
- Вернуть ингредиент на склад
- Отправить бункер на чистку

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "warehouse:history")
@with_error_handling
@role_required("warehouse", "admin")
async def view_history(callback: types.CallbackQuery):
    """Просмотр истории операций"""
    text = """
📜 <b>История операций</b>

Здесь будет отображаться:
- История приёмок товара
- История выдач бункеров
- История заполнений
- Все операции склада

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "warehouse:inventory")
@with_error_handling
@role_required("warehouse", "admin")
async def start_inventory(callback: types.CallbackQuery):
    """Начало инвентаризации"""
    text = """
📋 <b>Инвентаризация</b>

Функция инвентаризации позволяет:
- Пересчитать фактические остатки
- Выявить расхождения
- Скорректировать данные в системе
- Сформировать акт инвентаризации

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


# Экспорт роутера
__all__ = ['router']