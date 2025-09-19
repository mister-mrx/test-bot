import logging
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.keyboards.fsm_keyboards import (
    get_service_choice_keyboard, get_person_check_subservice_keyboard
)
from bot.lexicon.lexicon_ru import LEXICON, FSM_QUESTIONS
from bot.models.data_store import add_order
from bot.states.states import ApplicationStates
from bot.config import config
from bot.keyboards.menu_keyboards import create_main_menu_keyboard # Для кнопки "назад"

router = Router()

# Хэндлер для отмены в любом состоянии (глобальный)
@router.message(Command("cancel"))
@router.callback_query(F.data == "fsm_cancel")
async def cancel_handler(event: Message | CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        if isinstance(event, CallbackQuery):
            await event.answer()
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    
    message_to_send = LEXICON["fsm_cancel"]
    
    if isinstance(event, Message):
        await event.answer(
            message_to_send,
            reply_markup=ReplyKeyboardRemove(),
        )
    elif isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(
                message_to_send,
                reply_markup=None # Убираем клавиатуру
            )
        except: # Если не получилось отредактировать
             await event.message.answer(
                message_to_send,
                reply_markup=ReplyKeyboardRemove(),
            )
        await event.answer()


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

    # Обновляем состояние для следующего шага
    await state.set_state(ApplicationStates.answering_questions)
    # Сохраняем индекс текущего вопроса (начнем с 0)
    await state.update_data(question_index=0)

    # Задаем первый вопрос из конфигурируемого списка
    first_question = FSM_QUESTIONS[0]['text']
    await callback.message.edit_text(first_question)

    await callback.answer()


# Единый обработчик для всех вопросов из списка FSM_QUESTIONS
@router.message(ApplicationStates.answering_questions)
async def process_answer(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    question_index = data.get('question_index', 0)

    # Сохраняем ответ. Ключ берем из списка вопросов.
    question_key = FSM_QUESTIONS[question_index]['key']
    await state.update_data({question_key: message.text})

    # Переходим к следующему вопросу
    next_question_index = question_index + 1

    if next_question_index < len(FSM_QUESTIONS):
        # Если есть еще вопросы, задаем следующий
        await state.update_data(question_index=next_question_index)
        next_question_text = FSM_QUESTIONS[next_question_index]['text']
        await message.answer(next_question_text)
    else:
        # Вопросы закончились, завершаем FSM и отправляем заявку
        await state.update_data(user_name=message.from_user.full_name)
        user_data = await state.get_data()
        await state.clear()

        order_id = add_order(message.from_user.id, user_data)
        
        # --- Формирование и отправка уведомления ---
        user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
        
        summary_lines = [
            f"✅ *Новая заявка!* ID: `#{order_id}`",
            f"👤 *Клиент:* {user_info}",
            "---",
            f"▶️ *Выбранная услуга:* {user_data.get('service_category', 'Н/Д')}",
        ]

        # Добавляем ответы на вопросы
        for question in FSM_QUESTIONS:
            key = question['key']
            answer = user_data.get(key, 'Н/Д')
            # Используем > для цитирования, чтобы было нагляднее
            summary_lines.append(f"*{question['text']}*\n> {answer}")

        summary_text = "\n\n".join(summary_lines)

        # Отправка уведомления администратору
        try:
            await bot.send_message(config.MAIN_ADMIN_ID, summary_text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Failed to send message to main admin: {e}")

        # Отправка уведомления в групповой чат, если он указан
        if config.GROUP_CHAT_ID:
            try:
                await bot.send_message(config.GROUP_CHAT_ID, summary_text, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Failed to send message to group chat: {e}")

        await message.answer(
            LEXICON["fsm_finish"].format(order_id=order_id)
        )
