from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
# Импортируем FSM_SERVICES для динамического создания кнопок
from bot.lexicon.lexicon_ru import BUTTONS, FSM_SERVICES

# Клавиатуры, используемые в FSM для создания заявки.

def get_service_choice_keyboard() -> InlineKeyboardMarkup:
    """Динамически создает клавиатуру выбора основной услуги."""
    builder = InlineKeyboardBuilder()

    # Динамически создаем кнопки на основе словаря FSM_SERVICES
    for callback_data, service_info in FSM_SERVICES.items():
        builder.button(text=service_info['name'], callback_data=callback_data)

    # Добавляем кнопку "Назад в главное меню"
    builder.button(text=BUTTONS["back_to_main_menu"], callback_data="back_to_main_menu")
    builder.adjust(1) # По одной кнопке в ряд
    return builder.as_markup()

def get_subservice_choice_keyboard(service_key: str) -> InlineKeyboardMarkup:
    """Динамически создает клавиатуру выбора подуслуги для конкретной услуги."""
    builder = InlineKeyboardBuilder()
    
    sub_services = FSM_SERVICES.get(service_key, {}).get('sub_services', {})
    
    for callback_data, text in sub_services.items():
        builder.button(text=text, callback_data=callback_data)

    # Добавляем кнопку "Назад к выбору основной услуги"
    builder.button(text=BUTTONS["back"], callback_data="menu_create_task")
    builder.adjust(1)
    return builder.as_markup()
