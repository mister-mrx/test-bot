import logging
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.keyboards.fsm_keyboards import (
    get_service_choice_keyboard, get_subservice_choice_keyboard
)
from bot.lexicon.lexicon_ru import LEXICON, FSM_SERVICES, FSM_QUESTIONS
from bot.models.data_store import add_order
from bot.states.states import ApplicationStates
from bot.config import config

router = Router()

# ... (код cancel_handler и get_button_text без изменений)
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
                reply_markup=None
            )
        except:
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

# --- Начало FSM ---

# Этап 2: Выбор основной услуги
@router.callback_query(ApplicationStates.choosing_service, F.data.startswith("service_"))
async def process_service_choice(callback: CallbackQuery, state: FSMContext):
    service_key = callback.data
    service_info = FSM_SERVICES.get(service_key)

    if not service_info:
        await callback.answer("Ошибка: не удалось определить услугу.", show_alert=True)
        return
        
    await state.update_data(service_category=service_info['name'], service_key=service_key)

    # Проверяем, есть ли у этой услуги подуслуги
    if 'sub_services' in service_info:
        await state.set_state(ApplicationStates.choosing_subservice)
        keyboard = get_subservice_choice_keyboard(service_key)
        await callback.message.edit_text(LEXICON['sub_service_prompt'], reply_markup=keyboard)
    else:
        # Если подуслуг нет, сразу переходим к вопросам
        questions = FSM_QUESTIONS.get(service_key)
        if not questions:
            await callback.message.edit_text("Ошибка: для данной услуги не найдены вопросы.", reply_markup=None)
            await state.clear()
            return

        await state.set_state(ApplicationStates.answering_questions)
        await state.update_data(question_index=0, questions_key=service_key)
        await callback.message.edit_text(questions[0]['text'])

    await callback.answer()

# Этап 3: Выбор подуслуги
@router.callback_query(ApplicationStates.choosing_subservice, F.data.startswith("sub_"))
async def process_subservice_choice(callback: CallbackQuery, state: FSMContext):
    sub_service_key = callback.data
    sub_service_text = get_button_text(callback)

    if not sub_service_text:
        await callback.answer("Ошибка: не удалось определить подуслугу.", show_alert=True)
        return

    await state.update_data(sub_service_category=sub_service_text)

    questions = FSM_QUESTIONS.get(sub_service_key)
    if not questions:
        await callback.message.edit_text("Ошибка: для данной подуслуги не найдены вопросы.", reply_markup=None)
        await state.clear()
        return

    await state.set_state(ApplicationStates.answering_questions)
    await state.update_data(question_index=0, questions_key=sub_service_key)
    await callback.message.edit_text(questions[0]['text'])
    await callback.answer()


# Единый обработчик для всех вопросов из списка FSM_QUESTIONS
@router.message(ApplicationStates.answering_questions)
async def process_answer(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    question_index = data.get('question_index', 0)
    questions_key = data.get('questions_key')

    questions = FSM_QUESTIONS.get(questions_key, [])
    
    question_key = questions[question_index]['key']
    await state.update_data({question_key: message.text})

    next_question_index = question_index + 1

    if next_question_index < len(questions):
        await state.update_data(question_index=next_question_index)
        await message.answer(questions[next_question_index]['text'])
    else:
        user_data = await state.get_data()
        await state.clear()

        order_id = add_order(message.from_user.id, user_data)
        
        # --- Формирование и отправка уведомления ---
        user_info = f"@{message.from_user.username} [`{message.from_user.id}`]" if message.from_user.username else f"[`{message.from_user.id}`]"
        
        summary_lines = [
            LEXICON["new_application_header"].format(order_id=order_id),
            LEXICON["new_application_client"].format(user_info=user_info),
            "---",
            LEXICON["new_application_service"].format(service_category=user_data.get('service_category', 'Н/Д')),
        ]

        if 'sub_service_category' in user_data:
            summary_lines.append(LEXICON["new_application_sub_service"].format(sub_service_category=user_data['sub_service_category']))

        for question in questions:
            key = question['key']
            answer = user_data.get(key, 'Н/Д')
            summary_lines.append(f"*{question['text']}*\n> {answer}")

        summary_text = "\n\n".join(summary_lines)

        # Отправка уведомления только в групповой чат
        if config.GROUP_CHAT_ID:
            try:
                await bot.send_message(config.GROUP_CHAT_ID, summary_text, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Failed to send message to group chat {config.GROUP_CHAT_ID}: {e}")

        await message.answer(
            LEXICON["fsm_finish"].format(order_id=order_id)
        )