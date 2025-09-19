from aiogram.fsm.state import State, StatesGroup

# Состояния для процесса создания заявки
class ApplicationStates(StatesGroup):
    choosing_service = State()           # Выбор основной услуги
    choosing_subservice = State()        # Выбор подуслуги (досье)
    collecting_info_object = State()     # Сбор информации об объекте
    collecting_info_goal = State()       # Сбор информации о цели
    collecting_info_existing = State()   # Сбор имеющейся информации
    collecting_info_budget = State()     # Сбор информации о бюджете/сроках
    collecting_contact_name = State()    # Сбор имени пользователя
    collecting_contact_number = State()  # Сбор контактного номера
    collecting_contact_method = State()  # Выбор способа связи

# Состояния для админских действий
class AdminStates(StatesGroup):
    waiting_for_user_id_to_grant = State() # Ожидание ввода ID для выдачи прав