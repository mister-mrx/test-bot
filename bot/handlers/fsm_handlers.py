import logging
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.keyboards.fsm_keyboards import (
    get_service_choice_keyboard, get_person_check_subservice_keyboard,
    get_contact_method_keyboard
)
from bot.lexicon.lexicon_ru import LEXICON
from bot.models.data_store import add_order
from bot.states.states import ApplicationStates
from bot.config import config

router = Router()

# Хэндлер для отмены в любом состоянии (глобальный)
@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        LEXICON["fsm_cancel"],
        reply_markup=ReplyKeyboardRemove(),
    )

# --- Логика FSM (Адаптирована из вашего исходного кода) ---

# Вспомогательная функция для извлечения текста нажатой кнопки
def get_button_text(callback: CallbackQuery) -> Optional[str]:
    if callback.message.reply_markup:
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data == callback.data:
                    return btn.text
    return None

# Этап 2: Выбор основной услуги
@router.callback_query(ApplicationStates.choosing_service, F.data.startswith("service_"))
async def process_service_choice(callback: CallbackQuery, state: FSMContext):
    service_text = get_button_text(callback)
    if service_text:
        await state.update_data(service_category=service_text)

    if callback.data == "service_person_check":
        await callback.message.edit_text(
            "Выберите интересующую вас услугу."
        )
        await state.set_state(ApplicationStates.choosing_subservice)
        await callback.message.edit_reply_markup(reply_markup=get_person_check_subservice_keyboard())
    else:
        await callback.message.edit_text(
            "Вопрос 1: О ком или о чем необходимо собрать информацию?"
        )
        await state.set_state(ApplicationStates.collecting_info_object)
    await callback.answer()

# Этап 3: Выбор подуслуги
@router.callback_query(ApplicationStates.choosing_subservice, F.data.startswith("sub_"))
async def process_subservice_choice(callback: CallbackQuery, state: FSMContext):
    sub_service_text = get_button_text(callback)
    if sub_service_text:
        await state.update_data(sub_service=sub_service_text)

    await callback.message.edit_text(
        "Вопрос 1: О ком или о чем необходимо собрать информацию?"
    )
    await state.set_state(ApplicationStates.collecting_info_object)
    await callback.answer()

# Этапы 4 и 5: Сбор текстовой информации
@router.message(ApplicationStates.collecting_info_object)
async def process_info_object(message: Message, state: FSMContext):
    await state.update_data(object_info=message.text)
    await message.answer("Вопрос 2: Какова основная цель обращения?")
    await state.set_state(ApplicationStates.collecting_info_goal)

@router.message(ApplicationStates.collecting_info_goal)
async def process_info_goal(message: Message, state: FSMContext):
    await state.update_data(main_goal=message.text)
    await message.answer("Вопрос 3: Какая информация об объекте уже есть у вас?")
    await state.set_state(ApplicationStates.collecting_info_existing)

@router.message(ApplicationStates.collecting_info_existing)
async def process_info_existing(message: Message, state: FSMContext):
    await state.update_data(existing_info=message.text)
    await message.answer("Вопрос 4: Есть ли у вас бюджет и сроки?")
    await state.set_state(ApplicationStates.collecting_info_budget)

@router.message(ApplicationStates.collecting_info_budget)
async def process_info_budget(message: Message, state: FSMContext):
    await state.update_data(budget_timeline=message.text)
    await message.answer("Вопрос 5: Ваше имя.")
    await state.set_state(ApplicationStates.collecting_contact_name)

@router.message(ApplicationStates.collecting_contact_name)
async def process_contact_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Вопрос 6: Ваш номер телефона для связи.")
    await state.set_state(ApplicationStates.collecting_contact_number)

@router.message(ApplicationStates.collecting_contact_number)
async def process_contact_number(message: Message, state: FSMContext):
    await state.update_data(user_contact=message.text)
    await message.answer(
        "Вопрос 7: Как вам удобнее получить ответ?",
        reply_markup=get_contact_method_keyboard()
    )
    await state.set_state(ApplicationStates.collecting_contact_method)

# Финальный этап: Завершение сбора данных
@router.callback_query(ApplicationStates.collecting_contact_method, F.data.startswith("contact_"))
async def process_contact_method(callback: CallbackQuery, state: FSMContext, bot: Bot):
    preferred_method_text = get_button_text(callback)
    if preferred_method_text:
        await state.update_data(preferred_method=preferred_method_text)

    user_data = await state.get_data()
    await state.clear()

    # --- Сохранение заказа в БД (Временное хранилище) ---
    order_id = add_order(callback.from_user.id, user_data)

    # Формируем итоговое сообщение
    summary_text = (
        f"✅ Новая заявка! ID Заказа: #{order_id}\n\n"
        f"👤 Клиент: {user_data.get('user_name', 'Н/Д')}\n"
        # ... остальные детали ...
    )

    # Отправка уведомления Главному администратору
    try:
        await bot.send_message(config.MAIN_ADMIN_ID, summary_text)
    except Exception as e:
        logging.error(f"Failed to send message to main admin: {e}")

    # Благодарим пользователя
    await callback.message.edit_text(
        f"Спасибо! Ваша заявка принята (ID: #{order_id}). Введите /menu для возврата."
    )
    await callback.answer()