from aiogram.fsm.state import State, StatesGroup

# Состояния для процесса создания заявки
class ApplicationStates(StatesGroup):
    choosing_service = State()           # Выбор основной услуги
    choosing_subservice = State()        # Выбор подуслуги
    answering_questions = State()        # Единое состояние для ответов на вопросы

# Состояния для админских действий
class AdminStates(StatesGroup):
    waiting_for_user_id_to_grant = State() # Ожидание ввода ID для выдачи прав
