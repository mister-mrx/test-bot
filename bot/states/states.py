from aiogram.fsm.state import State, StatesGroup

# Состояния для процесса создания заявки
class ApplicationStates(StatesGroup):
    choosing_service = State()           # Выбор основной услуги
    choosing_subservice = State()        # Выбор подуслуги
    answering_questions = State()        # Единое состояние для ответов на вопросы

# Состояния для админских действий
class AdminStates(StatesGroup):
    waiting_for_user_id_to_grant = State() # Ожидание ввода ID для выдачи прав

# Состояния для управления заказами в админ-панели
class AdminOrderStates(StatesGroup):
    selecting_order = State()       # Ожидание ввода ID или номера заказа
    viewing_order = State()         # Просмотр конкретного заказа
    changing_status = State()       # Выбор нового статуса
    setting_name = State()          # Ожидание ввода нового названия
