from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

# Клавиатуры, используемые в FSM для создания заявки.

def get_service_choice_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="[Проверка физического лица]", callback_data="service_person_check")
    builder.button(text="[Due Diligence]", callback_data="service_due_diligence")
    builder.button(text="[Частное расследование]", callback_data="service_private_investigation")
    builder.button(text="[Другое]", callback_data="service_other")
    builder.adjust(1) # По одной кнопке в ряд
    return builder.as_markup()

def get_person_check_subservice_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="[Базовое досье (15 000 руб.)]", callback_data="sub_basic_dossier")
    builder.button(text="[Продвинутое досье (30 000 руб.)]", callback_data="sub_advanced_dossier")
    builder.button(text="[Полное досье (50 000 руб.)]", callback_data="sub_full_dossier")
    builder.button(text="[Не знаю, нужна консультация]", callback_data="sub_consultation_needed")
    builder.adjust(1)
    return builder.as_markup()

def get_contact_method_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="[Telegram]", callback_data="contact_telegram")
    builder.button(text="[WhatsApp]", callback_data="contact_whatsapp")
    builder.button(text="[Email]", callback_data="contact_email")
    builder.button(text="[Звонок]", callback_data="contact_call")
    builder.adjust(2) # По две кнопки в ряд
    return builder.as_markup()