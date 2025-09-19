from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from bot.lexicon.lexicon_ru import BUTTONS, LEXICON

def create_main_menu_keyboard(user_role: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру главного меню."""
    builder = InlineKeyboardBuilder()

    # Основные кнопки
    builder.button(text=BUTTONS["create_task"], callback_data="menu_create_task")
    builder.button(text=BUTTONS["my_cases"], callback_data="menu_my_cases")
    builder.button(text=BUTTONS["referral_program"], callback_data="menu_referral")

    # Кнопки со ссылками (F.A.Q. и Канал)
    builder.button(text=BUTTONS["faq"], url=LEXICON["faq_url"])
    builder.button(text=BUTTONS["channel"], url=LEXICON["channel_url"])

    # Админская кнопка (отображается только если у пользователя есть права)
    if user_role in ["admin", "main_admin"]:
        builder.button(text=BUTTONS["admin_options"], callback_data="menu_admin")

    # Расположение кнопок
    builder.adjust(1, 2, 2, 1)

    return builder.as_markup()

def create_referral_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру реферального меню."""
    builder = InlineKeyboardBuilder()
    builder.button(text=BUTTONS["my_referrals"], callback_data="referral_my_referrals")
    builder.button(text=BUTTONS["back"], callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def create_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру админ-панели."""
    builder = InlineKeyboardBuilder()
    builder.button(text=BUTTONS["admin_list_users"], callback_data="admin_list_users")
    builder.button(text=BUTTONS["admin_all_orders"], callback_data="admin_all_orders")
    # Кнопка выдачи прав (доступ контролируется фильтром в хэндлере)
    builder.button(text=BUTTONS["admin_grant"], callback_data="admin_grant")
    builder.button(text=BUTTONS["back"], callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def create_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад в админ-меню."""
    builder = InlineKeyboardBuilder()
    builder.button(text=BUTTONS["back"], callback_data="menu_admin")
    return builder.as_markup()