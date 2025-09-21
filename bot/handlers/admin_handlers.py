import html
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.lexicon.lexicon_ru import LEXICON, ORDER_STATUSES, FSM_QUESTIONS
from bot.models.data_store import (
    get_all_users, grant_admin_role, users_db, get_all_orders, get_order_by_id,
    update_order_status, update_order_name, get_user_data
)
from bot.keyboards.menu_keyboards import (
    create_admin_menu_keyboard, create_back_to_admin_keyboard,
    create_grant_admin_keyboard, create_admin_orders_keyboard,
    create_order_management_keyboard, create_status_selection_keyboard
)
from bot.states.states import AdminStates, AdminOrderStates
from bot.filters.roles import IsAdmin, IsMainAdmin

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

async def show_admin_menu(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    text = LEXICON["admin_menu_title"]
    keyboard = create_admin_menu_keyboard()
    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()

@router.message(Command("admin"))
@router.callback_query(F.data == "menu_admin")
async def admin_menu_handler(event: Message | CallbackQuery, state: FSMContext):
    await show_admin_menu(event, state)

@router.callback_query(F.data == "admin_list_users")
async def list_users_handler(callback: CallbackQuery):
    users = get_all_users()
    text = LEXICON["admin_list_users_title"].format(count=len(users)) if users else "В базе нет пользователей."
    if users:
        for user in users:
            display_name = f"@{html.escape(user['username'])}" if user.get('username') else "Без ника"
            text += f"- ID: <code>{user['user_id']}</code>, Ник: {display_name}, Роль: {user['role']}\n"
    keyboard = create_back_to_admin_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# --- УПРАВЛЕНИЕ ЗАКАЗАМИ ---

async def get_orders_list_text(orders: list) -> str:
    """Формирует текстовое представление списка заказов."""
    if not orders:
        return LEXICON["admin_no_orders_found"]
    
    text_lines = []
    for i, order in enumerate(orders, 1):
        status_display = ORDER_STATUSES.get(order['status'], order['status'])
        user_info = get_user_data(order['user_id'])
        user_display = f"@{user_info['username']}" if user_info and user_info.get('username') else f"ID: {order['user_id']}"
        order_name = f"<b>{html.escape(order['name'])}</b>" if order.get('name') else f"Заказ <code>{order['order_id']}</code>"
        
        text_lines.append(f"{i}. {order_name} от {user_display} - {status_display}")
    
    text_lines.append(f"\n{LEXICON['admin_orders_list_prompt']}")
    return "\n".join(text_lines)

async def show_all_orders(callback: CallbackQuery, state: FSMContext, page: int = 1):
    """Отображает список всех заказов с фильтрами и пагинацией."""
    data = await state.get_data()
    current_filter = data.get('order_filter')
    
    orders, total_pages = get_all_orders(status_filter=current_filter, page=page)
    
    text_filter = ORDER_STATUSES.get(current_filter, 'Все') if current_filter else 'Все'
    title = LEXICON["admin_all_orders_title"].format(filter=text_filter)
    orders_text = await get_orders_list_text(orders)
    
    full_text = f"{title}\n\n{orders_text}"
    
    keyboard = create_admin_orders_keyboard(total_pages, page, current_filter)
    
    await callback.message.edit_text(full_text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(AdminOrderStates.selecting_order)
    await state.update_data(current_orders_on_page=orders)
    await callback.answer()

@router.callback_query(F.data == "admin_all_orders")
async def all_orders_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(order_filter=None) # Сбрасываем фильтр
    await show_all_orders(callback, state, page=1)

@router.callback_query(F.data.startswith("admin_orders_page_"))
async def all_orders_page_handler(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    await show_all_orders(callback, state, page=page)

@router.callback_query(F.data.startswith("admin_filter_"))
async def all_orders_filter_handler(callback: CallbackQuery, state: FSMContext):
    filter_key = callback.data.split("_")[-1]
    status_filter = filter_key if filter_key != "all" else None
    await state.update_data(order_filter=status_filter)
    await show_all_orders(callback, state, page=1)

async def show_single_order(event: Message | CallbackQuery, state: FSMContext, order_id: str):
    """Показывает детали одного заказа и кнопки управления."""
    order = get_order_by_id(order_id)
    if not order:
        if isinstance(event, Message):
            await event.answer(LEXICON["admin_order_not_found"].format(order_id=order_id), parse_mode="HTML")
        return

    await state.set_state(AdminOrderStates.viewing_order)

    user_info_db = get_user_data(order['user_id'])
    user_info = f"@{user_info_db['username']} (<code>{order['user_id']}</code>)" if user_info_db and user_info_db.get('username') else f"ID: <code>{order['user_id']}</code>"
    
    details = order.get('details', {})
    q_and_a = []
    questions_list = FSM_QUESTIONS.get(details.get('questions_key'), [])
    for q in questions_list:
        answer = html.escape(details.get(q['key'], 'N/A'))
        q_and_a.append(f"<b>{html.escape(q['text'])}</b>\n&gt; {answer}")

    text = LEXICON["admin_order_details"].format(
        order_id=order['order_id'],
        name=html.escape(order.get('name') or "Без названия"),
        status=ORDER_STATUSES.get(order['status'], order['status']),
        user_info=user_info,
        service=html.escape(details.get('service_category', 'N/A')),
        sub_service=html.escape(details.get('sub_service_category', 'N/A')),
        questions_answers="\n\n".join(q_and_a)
    )
    keyboard = create_order_management_keyboard(order['order_id'])

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()

@router.callback_query(F.data.startswith("view_order_admin_"))
async def view_order_admin_handler(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split('_')[-1]
    await show_single_order(callback, state, order_id)

@router.message(AdminOrderStates.selecting_order)
async def process_order_selection(message: Message, state: FSMContext):
    data = await state.get_data()
    orders_on_page = data.get('current_orders_on_page', [])
    selection = message.text.strip()
    order_id = None

    if selection.isdigit():
        idx = int(selection) - 1
        if 0 <= idx < len(orders_on_page):
            order_id = orders_on_page[idx]['order_id']
    else:
        order = get_order_by_id(selection)
        if order:
            order_id = order['order_id']

    if order_id:
        await show_single_order(message, state, order_id)
    else:
        await message.answer(LEXICON["admin_order_not_found"].format(order_id=selection), parse_mode="HTML")

@router.callback_query(AdminOrderStates.viewing_order, F.data.startswith("manage_status_"))
async def change_status_handler(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split('_')[-1]
    await state.set_state(AdminOrderStates.changing_status)
    keyboard = create_status_selection_keyboard(order_id)
    text = LEXICON["admin_change_status_prompt"].format(order_id=order_id)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(AdminOrderStates.changing_status, F.data.startswith("set_status_"))
async def set_status_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    parts = callback.data.split('_')
    order_id = parts[2]
    new_status = "_".join(parts[3:])

    if update_order_status(order_id, new_status):
        order = get_order_by_id(order_id)
        client_id = order['user_id']
        status_display = ORDER_STATUSES.get(new_status, new_status)
        
        try:
            await bot.send_message(
                client_id,
                LEXICON["notification_status_changed"].format(order_id=order_id, status=status_display),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Failed to notify user {client_id}: {e}")

        # Создаем текст для всплывающего уведомления без HTML-тегов
        alert_text = LEXICON["admin_status_updated"].format(
            order_id=order_id, status=status_display
        ).replace("<code>", "").replace("</code>", "").replace("<b>", "").replace("</b>", "")

        await callback.answer(
            alert_text,
            show_alert=True
        )
    await show_single_order(callback, state, order_id)

@router.callback_query(AdminOrderStates.viewing_order, F.data.startswith("manage_name_"))
async def set_name_handler(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split('_')[-1]
    await state.update_data(order_id_to_rename=order_id)
    await state.set_state(AdminOrderStates.setting_name)
    text = LEXICON["admin_set_name_prompt"].format(order_id=order_id)
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.message(AdminOrderStates.setting_name)
async def process_new_name(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id_to_rename')
    new_name = message.text
    if order_id and update_order_name(order_id, new_name):
        order = get_order_by_id(order_id)
        client_id = order['user_id']
        
        try:
            await bot.send_message(
                client_id,
                LEXICON["notification_name_changed"].format(order_id=order_id, name=html.escape(new_name)),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Failed to notify user {client_id}: {e}")
            
        await message.answer(LEXICON["admin_name_updated"].format(order_id=order_id))
    await show_single_order(message, state, order_id)

# --- ВЫДАЧА ПРАВ АДМИНИСТРАТОРА ---

@router.message(Command("grant_admin"), IsMainAdmin())
async def cmd_grant_admin(message: Message, state: FSMContext):
    # ... (rest of the grant admin logic remains unchanged)
    args = message.text.split()
    if len(args) < 2:
        await message.answer(LEXICON["admin_grant_prompt"], reply_markup=create_grant_admin_keyboard())
        await state.set_state(AdminStates.waiting_for_user_id_to_grant)
        return
    try:
        user_id_to_grant = int(args[1])
        await process_grant(message, user_id_to_grant, state)
    except ValueError:
        await message.answer(LEXICON["admin_grant_invalid_id"])

@router.callback_query(F.data == "admin_grant", IsMainAdmin())
async def grant_admin_button_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        LEXICON["admin_grant_prompt"],
        reply_markup=create_grant_admin_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_user_id_to_grant)
    await callback.answer()

@router.message(StateFilter(AdminStates.waiting_for_user_id_to_grant), IsMainAdmin())
async def process_grant_admin_id(message: Message, state: FSMContext):
    try:
        user_id_to_grant = int(message.text)
        await process_grant(message, user_id_to_grant, state)
    except ValueError:
        await message.answer(LEXICON["admin_grant_invalid_id"])

async def process_grant(message: Message, user_id_to_grant: int, state: FSMContext):
    if user_id_to_grant not in users_db:
        await message.answer(LEXICON["admin_user_not_found"].format(user_id=user_id_to_grant))
        return
    if grant_admin_role(user_id_to_grant):
        await message.answer(LEXICON["admin_grant_success"].format(user_id=user_id_to_grant))
        await show_admin_menu(message, state)
    else:
        await message.answer("Не удалось выдать права (возможно, пользователь уже Главный админ).")

@router.message(Command("grant_admin"))
@router.callback_query(F.data == "admin_grant")
async def access_denied_main_admin(event: Message | CallbackQuery):
    text = LEXICON["admin_only_main_can_grant"]
    if isinstance(event, Message):
        await event.answer(text)
    else:
        await event.answer(text, show_alert=True)


