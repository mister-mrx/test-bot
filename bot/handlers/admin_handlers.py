from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.lexicon.lexicon_ru import LEXICON
from bot.models.data_store import get_all_users, grant_admin_role, users_db
from bot.keyboards.menu_keyboards import (
    create_admin_menu_keyboard, create_back_to_admin_keyboard
)
from bot.states.states import AdminStates
# Импортируем кастомные фильтры
from bot.filters.roles import IsAdmin, IsMainAdmin

router = Router()

# Применяем фильтр IsAdmin ко всему роутеру. Все хэндлеры ниже требуют прав админа.
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# Вспомогательная функция для отображения админ-меню
async def show_admin_menu(event: Message | CallbackQuery, state: FSMContext):
    await state.clear() # Сбрасываем админские состояния (например, ввод ID)
    text = LEXICON["admin_menu_title"]
    keyboard = create_admin_menu_keyboard()

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()

# Хэндлер на команду /admin и кнопку "Админ. опции"
@router.message(Command("admin"))
@router.callback_query(F.data == "menu_admin")
async def admin_menu_handler(event: Message | CallbackQuery, state: FSMContext):
    await show_admin_menu(event, state)

# Хэндлер для кнопки "Список пользователей 👥"
@router.callback_query(F.data == "admin_list_users")
async def list_users_handler(callback: CallbackQuery):
    users = get_all_users()
    if not users:
        text = "В базе нет пользователей."
    else:
        text = LEXICON["admin_list_users_title"].format(count=len(users))
        for user in users:
            display_name = f"@{user.get('username')}" if user.get('username') else "Без ника"
            # Используем Markdown для ID
            text += f"- ID: `{user['user_id']}`, Ник: {display_name}, Роль: {user['role']}\n"

    keyboard = create_back_to_admin_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# Хэндлер для кнопки "Все заказы 📦" (Заглушка)
@router.callback_query(F.data == "admin_all_orders")
async def all_orders_handler(callback: CallbackQuery):
    # TODO: Реализовать просмотр заказов и кнопку "Добавить файл"
    await callback.answer(LEXICON["admin_all_orders_title"], show_alert=True)

# --- Выдача прав администратора (Только Главный Админ) ---

# 1. Хэндлер на команду /grant_admin <user_id>. Используем фильтр IsMainAdmin.
@router.message(Command("grant_admin"), IsMainAdmin())
async def cmd_grant_admin(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) < 2:
        # Если ID не указан в команде, запускаем FSM для запроса ID
        await message.answer(LEXICON["admin_grant_prompt"])
        await state.set_state(AdminStates.waiting_for_user_id_to_grant)
        return

    try:
        user_id_to_grant = int(args[1])
        await process_grant(message, user_id_to_grant, state)
    except ValueError:
        await message.answer(LEXICON["admin_grant_invalid_id"])


# 2. Хэндлер для кнопки "Выдать админку 🛠". Используем фильтр IsMainAdmin.
@router.callback_query(F.data == "admin_grant", IsMainAdmin())
async def grant_admin_button_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(LEXICON["admin_grant_prompt"])
    await state.set_state(AdminStates.waiting_for_user_id_to_grant)
    await callback.answer()

# 3. Хэндлер для обработки введенного ID в состоянии FSM. Используем фильтр IsMainAdmin.
@router.message(StateFilter(AdminStates.waiting_for_user_id_to_grant), IsMainAdmin())
async def process_grant_admin_id(message: Message, state: FSMContext):
    try:
        user_id_to_grant = int(message.text)
        await process_grant(message, user_id_to_grant, state)

    except ValueError:
        await message.answer(LEXICON["admin_grant_invalid_id"])
        # Не сбрасываем состояние, позволяем пользователю ввести ID заново

async def process_grant(message: Message, user_id_to_grant: int, state: FSMContext):
    """Логика выдачи прав."""
    # Проверяем существование пользователя перед выдачей прав
    if user_id_to_grant not in users_db:
            await message.answer(LEXICON["admin_user_not_found"].format(user_id=user_id_to_grant))
            return

    if grant_admin_role(user_id_to_grant):
        await message.answer(LEXICON["admin_grant_success"].format(user_id=user_id_to_grant))
        # Возвращаемся в админ-меню после успеха (и сбрасываем состояние)
        await show_admin_menu(message, state)
    else:
        await message.answer("Не удалось выдать права (возможно, пользователь уже Главный админ).")


# Обработчик ошибки доступа для тех админов, кто не является Главным
# Сработает, если предыдущие хэндлеры с фильтром IsMainAdmin не прошли проверку, но IsAdmin (фильтр роутера) прошел.
@router.message(Command("grant_admin"))
@router.callback_query(F.data == "admin_grant")
async def access_denied_main_admin(event: Message | CallbackQuery):
    text = LEXICON["admin_only_main_can_grant"]
    if isinstance(event, Message):
        await event.answer(text)
    else:
        await event.answer(text, show_alert=True)