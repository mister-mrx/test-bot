from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from math import ceil
# Импортируем утилиты для работы с реферальными ссылками
from aiogram.utils.deep_linking import decode_payload, create_start_link

from bot.lexicon.lexicon_ru import LEXICON, USER_ROLES, BUTTONS
from bot.models.data_store import (
    register_user, get_user_data, get_orders_count, get_user_role,
    get_referrals, get_user_orders
)
from bot.keyboards.menu_keyboards import (
    create_main_menu_keyboard, create_referral_menu_keyboard,
    create_my_orders_keyboard, create_referrals_keyboard
)
from bot.states.states import ApplicationStates

router = Router()

# Вспомогательная функция для отображения главного меню
async def show_main_menu(event: Message | CallbackQuery, state: FSMContext):
    await state.clear() # Сбрасываем любое текущее состояние FSM

    user_id = event.from_user.id
    # Убедимся, что пользователь зарегистрирован
    if not get_user_data(user_id):
        register_user(user_id, event.from_user.username)

    # Получаем данные для отображения в меню
    role_key = get_user_role(user_id)
    role_display = USER_ROLES.get(role_key, "Неизвестно")
    orders_count = get_orders_count(user_id)

    # Формируем текст меню, используя Markdown для форматирования ID
    text = LEXICON["main_menu_text"].format(
        user_id=user_id,
        role=role_display,
        orders_count=orders_count
    )

    # Передаем роль для динамического отображения кнопки "Админ. опции"
    keyboard = create_main_menu_keyboard(role_key)

    # Отправляем или редактируем сообщение
    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    elif isinstance(event, CallbackQuery):
        try:
            # Указываем parse_mode="Markdown"
            await event.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception:
            # Игнорируем ошибку, если сообщение не изменилось
            pass
        await event.answer()

# Хэндлер на команду /start (обрабатывает регистрацию и реферальные ссылки)
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    args = message.text.split()
    referrer_id = None
    is_new_user = False

    # Проверяем, есть ли пользователь в базе ДО регистрации
    if not get_user_data(message.from_user.id):
        is_new_user = True
        # Проверяем наличие аргументов (для реферальной ссылки)
        if len(args) > 1:
            try:
                # Декодируем payload.
                payload = decode_payload(args[1])
                if payload.startswith("ref_"):
                    referrer_id = int(payload.split("_")[1])
            except Exception:
                # Если аргумент некорректный или не декодируется, игнорируем его
                pass

    # Регистрируем пользователя. Функция вернет ID реферера, если он был присвоен.
    assigned_referrer_id = register_user(message.from_user.id, message.from_user.username, referrer_id if is_new_user else None)

    # Если пользователь новый и ему был присвоен реферер, отправляем уведомление
    if is_new_user and assigned_referrer_id:
        try:
            new_ref_username = f"@{message.from_user.username}" if message.from_user.username else f"ID: `{message.from_user.id}`"
            await bot.send_message(
                assigned_referrer_id,
                LEXICON["new_referral_notification"].format(new_referral_info=new_ref_username),
                parse_mode="Markdown"
            )
        except Exception as e:
            # Логируем ошибку, если не смогли уведомить
            print(f"Failed to notify referrer {assigned_referrer_id}: {e}")


    # Показываем главное меню
    await show_main_menu(message, state)

# Хэндлер на команду /menu и кнопку "Главное меню" (если бы она была не Inline)
@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await show_main_menu(message, state)

# Хэндлер для кнопки "Назад в главное меню"
@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await show_main_menu(callback, state)

# Хэндлер для кнопки "Создать заявку" (/task)
@router.message(Command("task"))
@router.callback_query(F.data == "menu_create_task")
async def create_task_handler(event: Message | CallbackQuery, state: FSMContext):
    # Запускаем FSM процесс создания заявки
    await state.set_state(ApplicationStates.choosing_service)

    # Импортируем клавиатуру FSM
    from bot.keyboards.fsm_keyboards import get_service_choice_keyboard
    keyboard = get_service_choice_keyboard()
    text = LEXICON["fsm_start_prompt"]

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()

# --- Логика раздела "Мои заказы" ---

@router.message(Command("cases"))
@router.callback_query(F.data == "menu_my_cases")
async def my_cases_handler(event: Message | CallbackQuery):
    user_id = event.from_user.id
    orders, total_pages = get_user_orders(user_id, page=1)

    text = LEXICON["my_cases_title"]
    keyboard = create_my_orders_keyboard(orders, total_pages, current_page=1)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()

@router.callback_query(F.data.startswith("orders_page_"))
async def process_orders_pagination(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    orders, total_pages = get_user_orders(user_id, page=page)

    text = LEXICON["my_cases_title"]
    keyboard = create_my_orders_keyboard(orders, total_pages, current_page=page)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# Хэндлер для кнопки "Реферальная программа" (/referral)
@router.message(Command("referral"))
@router.callback_query(F.data == "menu_referral")
async def referral_handler(event: Message | CallbackQuery, bot: Bot):
    user_id = event.from_user.id

    # Генерируем реферальную ссылку с помощью утилит Aiogram.
    # Мы передаем payload "ref_{user_id}" и используем encode=True для надежности.
    # Это соответствует формату [https://t.me/MyBot?start=](https://t.me/MyBot?start=)<encoded_payload>
    link = await create_start_link(bot, f"ref_{user_id}", encode=True)

    # Форматируем текст, используя Markdown для моноширинного текста (backticks)
    text = LEXICON["referral_link_text"].format(referral_link=link)
    keyboard = create_referral_menu_keyboard()

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    elif isinstance(event, CallbackQuery):
        # Указываем parse_mode="Markdown"
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await event.answer()

# --- Логика раздела "Мои рефералы" ---

@router.callback_query(F.data == "referral_my_referrals")
async def my_referrals_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    referrals, total_pages = get_referrals(user_id, page=1)

    if not referrals:
        await callback.answer(LEXICON["no_referrals_yet"], show_alert=True)
        return

    text_lines = [LEXICON["my_referrals_title"]]
    for i, ref in enumerate(referrals, 1):
        display_name = f"@{ref.get('username')}" if ref.get('username') else f"ID: {ref['user_id']}"
        text_lines.append(f"{i}. {display_name}")

    text = "\n".join(text_lines)
    keyboard = create_referrals_keyboard(current_page=1, total_pages=total_pages)
    
    # Отправляем сообщение в чат вместо alert
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("ref_page_"))
async def process_referrals_pagination(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    referrals, total_pages = get_referrals(user_id, page=page)

    text_lines = [LEXICON["my_referrals_title"]]
    start_index = (page - 1) * 10 + 1 # 10 рефералов на странице
    for i, ref in enumerate(referrals, start_index):
        display_name = f"@{ref.get('username')}" if ref.get('username') else f"ID: {ref['user_id']}"
        text_lines.append(f"{i}. {display_name}")

    text = "\n".join(text_lines)
    keyboard = create_referrals_keyboard(current_page=page, total_pages=total_pages)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
