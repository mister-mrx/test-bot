from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from bot.lexicon.lexicon_ru import BUTTONS, LEXICON
from math import ceil

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
    builder.button(text=BUTTONS["back_to_main_menu"], callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def create_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру админ-панели."""
    builder = InlineKeyboardBuilder()
    builder.button(text=BUTTONS["admin_list_users"], callback_data="admin_list_users")
    builder.button(text=BUTTONS["admin_all_orders"], callback_data="admin_all_orders")
    # Кнопка выдачи прав (доступ контролируется фильтром в хэндлере)
    builder.button(text=BUTTONS["admin_grant"], callback_data="admin_grant")
    builder.button(text=BUTTONS["back_to_main_menu"], callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def create_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад в админ-меню."""
    builder = InlineKeyboardBuilder()
    builder.button(text=BUTTONS["back"], callback_data="menu_admin")
    return builder.as_markup()

def create_grant_admin_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад в админ-меню для процесса выдачи прав."""
    builder = InlineKeyboardBuilder()
    builder.button(text=BUTTONS["back_to_admin_menu"], callback_data="menu_admin")
    return builder.as_markup()


def create_my_orders_keyboard(orders: list, total_pages: int, current_page: int = 1) -> InlineKeyboardMarkup:
    """Создает клавиатуру для списка заказов с пагинацией."""
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки с заказами
    if orders:
        for order in orders:
            order_text = f"#{order['order_id']} - {order['status']}"
            builder.button(text=order_text, callback_data=f"view_order_{order['order_id']}")
        builder.adjust(1)

    # Логика пагинации
    if total_pages > 1:
        pagination_buttons = []
        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(text=BUTTONS["prev_page"], callback_data=f"orders_page_{current_page - 1}")
            )
        
        pagination_buttons.append(
            InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="dummy_page_display")
        )

        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(text=BUTTONS["next_page"], callback_data=f"orders_page_{current_page + 1}")
            )
        builder.row(*pagination_buttons)

    builder.row(InlineKeyboardButton(text=BUTTONS["back_to_main_menu"], callback_data="back_to_main_menu"))
    return builder.as_markup()

def create_referrals_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для пагинации списка рефералов."""
    builder = InlineKeyboardBuilder()

    if total_pages > 1:
        pagination_buttons = []
        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(text=BUTTONS["prev_page"], callback_data=f"ref_page_{current_page - 1}")
            )
        
        pagination_buttons.append(
            InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="dummy_page_display")
        )

        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(text=BUTTONS["next_page"], callback_data=f"ref_page_{current_page + 1}")
            )
        builder.row(*pagination_buttons)
    
    # Кнопка назад в реферальное меню
    builder.row(InlineKeyboardButton(text=BUTTONS["back"], callback_data="menu_referral"))
    return builder.as_markup()
