from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
# Импортируем утилиты для работы с реферальными ссылками
from aiogram.utils.deep_linking import decode_payload, create_start_link

from bot.lexicon.lexicon_ru import LEXICON, USER_ROLES
from bot.models.data_store import (
    register_user, get_user_data, get_orders_count, get_user_role,
    get_referrals
)
from bot.keyboards.menu_keyboards import (
    create_main_menu_keyboard, create_referral_menu_keyboard
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
async def cmd_start(message: Message, state: FSMContext):
    args = message.text.split()
    referrer_id = None

    # Проверяем наличие аргументов (для реферальной ссылки)
    if len(args) > 1:
        try:
            # Декодируем payload. Так как мы используем create_start_link с encode=True,
            # необходимо использовать decode_payload.
            payload = decode_payload(args[1])
            if payload.startswith("ref_"):
                referrer_id = int(payload.split("_")[1])
        except Exception:
            # Если аргумент некорректный или не декодируется, игнорируем его
            pass

    # Регистрируем пользователя
    register_user(message.from_user.id, message.from_user.username, referrer_id)

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

# Хэндлер для кнопки "Мои заказы" (/cases) - Заглушка
@router.message(Command("cases"))
@router.callback_query(F.data == "menu_my_cases")
async def my_cases_handler(event: Message | CallbackQuery):
    text = LEXICON["my_cases_placeholder"]
    # TODO: Реализовать логику отображения заказов

    if isinstance(event, Message):
        await event.answer(text)
    elif isinstance(event, CallbackQuery):
        # Показываем как всплывающее уведомление (alert)
        await event.answer(text, show_alert=True)


# Хэндлер для кнопки "Реферальная программа" (/referral)
@router.message(Command("referral"))
@router.callback_query(F.data == "menu_referral")
async def referral_handler(event: Message | CallbackQuery, bot: Bot):
    user_id = event.from_user.id

    # Генерируем реферальную ссылку с помощью утилит Aiogram.
    # Мы передаем payload "ref_{user_id}" и используем encode=True для надежности.
    # Это соответствует формату https://t.me/MyBot?start=<encoded_payload>
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

# Хэндлер для кнопки "Мои рефералы 📊"
@router.callback_query(F.data == "referral_my_referrals")
async def my_referrals_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    referrals = get_referrals(user_id)

    if not referrals:
        text = LEXICON["no_referrals_yet"]
    else:
        text = LEXICON["my_referrals_title"] + "\n\n"
        for i, ref in enumerate(referrals, 1):
            # Отображаем username или ID, если username нет
            display_name = f"@{ref.get('username')}" if ref.get('username') else f"ID: {ref['user_id']}"
            text += f"{i}. {display_name}\n"

    # Показываем список во всплывающем окне
    await callback.answer(text, show_alert=True)