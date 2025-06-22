"""
Обработчики для роли Оператор
"""
import logging
from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.models.user import User
from backend.models.machine import Machine, MachineStatus
from backend.models.hopper import Hopper, HopperStatus
from backend.models.operations import Operation, OperationType
from backend.bot.keyboards.menus import get_operator_menu, get_back_button
from backend.bot.utils.decorators import role_required, with_error_handling
from backend.bot.utils.helpers import escape_html, format_datetime

logger = logging.getLogger(__name__)
router = Router(name="operator")


@router.callback_query(F.data == "operator:tasks")
@with_error_handling
@role_required("operator", "admin")
async def operator_tasks(callback: types.CallbackQuery, user: User, session: AsyncSession):
    """Главное меню оператора с заданиями"""
    # Получаем статистику
    
    # Назначенные автоматы
    assigned_machines = await session.scalar(
        select(func.count(Machine.id))
        .where(Machine.assigned_operator_id == user.id)
    )
    
    # Активные автоматы
    active_machines = await session.scalar(
        select(func.count(Machine.id))
        .where(
            Machine.assigned_operator_id == user.id,
            Machine.status == MachineStatus.ACTIVE
        )
    )
    
    # Назначенные бункеры
    assigned_hoppers = await session.scalar(
        select(func.count(Hopper.id))
        .where(
            Hopper.assigned_operator_id == user.id,
            Hopper.status == HopperStatus.FILLED
        )
    )
    
    # Установленные бункеры
    installed_hoppers = await session.scalar(
        select(func.count(Hopper.id))
        .where(
            Hopper.assigned_operator_id == user.id,
            Hopper.status == HopperStatus.INSTALLED
        )
    )
    
    # Операции за сегодня
    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    today_operations = await session.scalar(
        select(func.count(Operation.id))
        .where(
            Operation.user_id == user.id,
            Operation.created_at >= today_start
        )
    )
    
    text = f"""
🔧 <b>Задания оператора</b>

Оператор: {escape_html(user.full_name)}

<b>📊 Текущие показатели:</b>
- Автоматов назначено: {assigned_machines} (активных: {active_machines})
- Бункеров к установке: {assigned_hoppers}
- Бункеров установлено: {installed_hoppers}
- Операций сегодня: {today_operations}

Выберите действие:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_operator_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "operator:machines")
@with_error_handling
@role_required("operator", "admin")
async def view_machines(callback: types.CallbackQuery, user: User, session: AsyncSession):
    """Просмотр назначенных автоматов"""
    # Получаем назначенные автоматы
    stmt = select(Machine).where(
        Machine.assigned_operator_id == user.id
    ).order_by(Machine.code)
    
    result = await session.execute(stmt)
    machines = result.scalars().all()
    
    if not machines:
        await callback.answer("У вас нет назначенных автоматов", show_alert=True)
        return
    
    text = "🏭 <b>Ваши автоматы</b>\n\n"
    
    for machine in machines:
        # Статус эмодзи
        status_emoji = {
            MachineStatus.ACTIVE: "🟢",
            MachineStatus.MAINTENANCE: "🟡",
            MachineStatus.BROKEN: "🔴",
            MachineStatus.INACTIVE: "⚫"
        }.get(machine.status, "⚪")
        
        # Количество установленных бункеров
        hopper_count = await session.scalar(
            select(func.count(Hopper.id))
            .where(
                Hopper.machine_id == machine.id,
                Hopper.status == HopperStatus.INSTALLED
            )
        )
        
        text += (
            f"{status_emoji} <b>{machine.code}</b> - {escape_html(machine.name)}\n"
            f"📍 {escape_html(machine.display_location)}\n"
            f"📦 Бункеров: {hopper_count}/4\n"
        )
        
        # Дата последнего обслуживания
        if machine.last_service_date:
            days_ago = (datetime.now() - machine.last_service_date).days
            text += f"🔧 Обслуживание: {days_ago} дн. назад\n"
            
            if days_ago > 30:
                text += "⚠️ <i>Требуется обслуживание!</i>\n"
        
        text += "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "operator:stats")
@with_error_handling
@role_required("operator", "admin")
async def view_stats(callback: types.CallbackQuery, user: User, session: AsyncSession):
    """Просмотр статистики оператора"""
    # Получаем статистику за разные периоды
    now = datetime.now()
    
    # За сегодня
    today_start = now.replace(hour=0, minute=0, second=0)
    today_ops = await session.scalar(
        select(func.count(Operation.id))
        .where(
            Operation.user_id == user.id,
            Operation.created_at >= today_start
        )
    )
    
    # За неделю
    week_start = now - timedelta(days=7)
    week_ops = await session.scalar(
        select(func.count(Operation.id))
        .where(
            Operation.user_id == user.id,
            Operation.created_at >= week_start
        )
    )
    
    # За месяц
    month_start = now.replace(day=1, hour=0, minute=0, second=0)
    month_ops = await session.scalar(
        select(func.count(Operation.id))
        .where(
            Operation.user_id == user.id,
            Operation.created_at >= month_start
        )
    )
    
    # По типам операций за месяц
    stmt = select(
        Operation.operation_type,
        func.count(Operation.id)
    ).where(
        Operation.user_id == user.id,
        Operation.created_at >= month_start
    ).group_by(Operation.operation_type)
    
    result = await session.execute(stmt)
    operations_by_type = result.all()
    
    text = f"""
📊 <b>Ваша статистика</b>

<b>Операций выполнено:</b>
- Сегодня: {today_ops}
- За неделю: {week_ops}
- За месяц: {month_ops}

<b>По типам за месяц:</b>
"""
    
    type_names = {
        OperationType.HOPPER_INSTALL: "Установка бункеров",
        OperationType.HOPPER_REMOVE: "Снятие бункеров",
        OperationType.MACHINE_SERVICE: "Обслуживание",
        OperationType.PROBLEM_REPORT: "Отчеты о проблемах"
    }
    
    for op_type, count in operations_by_type:
        name = type_names.get(op_type, op_type)
        text += f"• {name}: {count}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "operator:install")
@with_error_handling
@role_required("operator", "admin")
async def start_install(callback: types.CallbackQuery):
    """Начало процесса установки бункера"""
    text = """
📦 <b>Установка бункера</b>

Процесс установки:
1. Выберите бункер из назначенных вам
2. Выберите автомат для установки
3. Установите бункер физически
4. Сделайте фото для подтверждения

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "operator:remove")
@with_error_handling
@role_required("operator", "admin")
async def start_remove(callback: types.CallbackQuery):
    """Начало процесса снятия бункера"""
    text = """
📤 <b>Снятие бункера</b>

Процесс снятия:
1. Выберите автомат
2. Выберите бункер для снятия
3. Взвесьте бункер с остатками
4. Сделайте фото
5. Верните бункер на склад

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "operator:service")
@with_error_handling
@role_required("operator", "admin")
async def start_service(callback: types.CallbackQuery):
    """Начало процесса обслуживания"""
    text = """
🔧 <b>Обслуживание автомата</b>

Виды обслуживания:
- Плановое ТО
- Чистка
- Мелкий ремонт
- Замена расходников

С фотофиксацией выполненных работ.

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "operator:report")
@with_error_handling
@role_required("operator", "admin")
async def start_report(callback: types.CallbackQuery):
    """Начало создания отчета о проблеме"""
    text = """
⚠️ <b>Сообщить о проблеме</b>

Типы проблем:
- Поломка автомата
- Проблема с бункером
- Нехватка ингредиентов
- Другое

Обязательна фотофиксация проблемы.

<i>Полная реализация будет добавлена в следующем обновлении</i>
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button()
    )
    await callback.answer()


# Экспорт роутера
__all__ = ['router']