from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from .menu_keyboards import BUTTONS

# Клавиатуры, используемые в FSM для создания заявки.

def get_service_choice_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="[Проверка физического лица]", callback_data="service_person_check")
    builder.button(text="[Due Diligence]", callback_data="service_due_diligence")
    builder.button(text="[Частное расследование]", callback_data="service_private_investigation")
    builder.button(text="[Другое]", callback_data="service_other")
    # Добавляем кнопку "Назад в главное меню"
    builder.button(text=BUTTONS["back_to_main_menu"], callback_data="back_to_main_menu")
    builder.adjust(1) # По одной кнопке в ряд
    return builder.as_markup()

def get_person_check_subservice_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="[Базовое досье (15 000 руб.)]", callback_data="sub_basic_dossier")
    builder.button(text="[Продвинутое досье (30 000 руб.)]", callback_data="sub_advanced_dossier")
    builder.button(text="[Полное досье (50 000 руб.)]", callback_data="sub_full_dossier")
    builder.button(text="[Не знаю, нужна консультация]", callback_data="sub_consultation_needed")
    # Добавляем кнопку "Назад к выбору услуги"
    builder.button(text=BUTTONS["back"], callback_data="menu_create_task")
    builder.adjust(1)
    return builder.as_markup()

# Эта клавиатура больше не нужна, так как способ связи не запрашивается
# def get_contact_method_keyboard() -> InlineKeyboardMarkup:
#     ...
