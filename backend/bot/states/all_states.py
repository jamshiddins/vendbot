"""
FSM состояния для всех ролей и процессов
"""
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Состояния для администратора"""
    
    # Поиск пользователей
    search_user = State()
    view_user = State()
    
    # Управление пользователями
    block_user_confirm = State()
    unblock_user_confirm = State()


class OwnerStates(StatesGroup):
    """Состояния для владельца (управление ролями)"""
    
    # Управление ролями
    manage_roles = State()
    add_role = State()
    remove_role = State()
    promote_admin = State()


class WarehouseStates(StatesGroup):
    """Состояния для склада"""
    
    # Приёмка товара
    receive_select_ingredient = State()
    receive_enter_quantity = State()
    receive_confirm = State()
    
    # Выдача бункеров
    issue_select_hopper = State()
    issue_select_operator = State()
    issue_confirm = State()
    
    # Заполнение бункеров
    fill_select_hopper = State()
    fill_select_ingredient = State()
    fill_weigh_empty = State()
    fill_weigh_full = State()
    fill_confirm = State()
    
    # Возврат бункеров
    return_select_hopper = State()
    return_weigh = State()
    return_confirm = State()
    
    # Инвентаризация
    inventory_select_ingredient = State()
    inventory_enter_quantity = State()
    inventory_confirm = State()


class OperatorStates(StatesGroup):
    """Состояния для оператора"""
    
    # Установка бункера
    install_select_hopper = State()
    install_select_machine = State()
    install_take_photo = State()
    install_confirm = State()
    
    # Снятие бункера
    remove_select_machine = State()
    remove_select_hopper = State()
    remove_weigh = State()
    remove_take_photo = State()
    remove_confirm = State()
    
    # Обслуживание
    service_select_machine = State()
    service_select_type = State()
    service_description = State()
    service_take_photo = State()
    service_confirm = State()
    
    # Отчет о проблеме
    report_select_machine = State()
    report_select_problem = State()
    report_description = State()
    report_take_photo = State()
    report_confirm = State()


class DriverStates(StatesGroup):
    """Состояния для водителя"""
    
    # Начало поездки
    start_trip_confirm = State()
    start_trip_vehicle = State()
    start_trip_odometer = State()
    start_trip_photo = State()
    
    # Завершение поездки
    end_trip_odometer = State()
    end_trip_photo = State()
    end_trip_confirm = State()
    
    # Заправка
    fuel_select_type = State()
    fuel_enter_amount = State()
    fuel_enter_cost = State()
    fuel_take_photo = State()
    fuel_confirm = State()
    
    # Маршрут
    route_add_point = State()
    route_confirm = State()


class CommonStates(StatesGroup):
    """Общие состояния"""
    
    # Регистрация
    registration_name = State()
    registration_phone = State()
    registration_confirm = State()
    
    # Настройки
    settings_menu = State()
    settings_change_name = State()
    settings_change_phone = State()
    
    # Обратная связь
    feedback_type = State()
    feedback_message = State()
    feedback_confirm = State()


# Вспомогательные функции

def get_state_description(state: State) -> str:
    """
    Возвращает описание состояния
    """
    descriptions = {
        # Admin
        AdminStates.search_user: "Поиск пользователя",
        AdminStates.view_user: "Просмотр пользователя",
        AdminStates.block_user_confirm: "Подтверждение блокировки",
        AdminStates.unblock_user_confirm: "Подтверждение разблокировки",
        
        # Warehouse
        WarehouseStates.receive_select_ingredient: "Выбор ингредиента для приёмки",
        WarehouseStates.receive_enter_quantity: "Ввод количества",
        WarehouseStates.receive_confirm: "Подтверждение приёмки",
        WarehouseStates.fill_select_hopper: "Выбор бункера для заполнения",
        WarehouseStates.fill_select_ingredient: "Выбор ингредиента",
        WarehouseStates.fill_weigh_empty: "Взвешивание пустого",
        WarehouseStates.fill_weigh_full: "Взвешивание полного",
        
        # Operator
        OperatorStates.install_select_hopper: "Выбор бункера для установки",
        OperatorStates.install_select_machine: "Выбор автомата",
        OperatorStates.install_take_photo: "Фото установки",
        OperatorStates.install_confirm: "Подтверждение установки",
        
        # Driver
        DriverStates.start_trip_vehicle: "Выбор автомобиля",
        DriverStates.start_trip_odometer: "Ввод показаний одометра",
        DriverStates.start_trip_photo: "Фото одометра",
        DriverStates.fuel_select_type: "Выбор типа топлива",
        DriverStates.fuel_enter_amount: "Ввод количества топлива",
        DriverStates.fuel_take_photo: "Фото чека",
    }
    
    return descriptions.get(state, str(state))


# Экспорт всех состояний
__all__ = [
    'AdminStates',
    'OwnerStates',
    'WarehouseStates',
    'OperatorStates',
    'DriverStates',
    'CommonStates',
    'get_state_description'
]