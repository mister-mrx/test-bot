# Определения ролей пользователей (Легко редактировать)
USER_ROLES: dict[str, str] = {
    "client": "Клиент 👤",
    "admin": "Администратор 🛠️",
    "main_admin": "Главный администратор 👑"
}

# --- Статусы заказов (Легко редактировать) ---
# Ключ: внутреннее имя статуса, Значение: отображаемое имя
ORDER_STATUSES: dict[str, str] = {
    "new": "Новый 🔵",
    "in_progress": "В работе 🔄",
    "completed": "Завершен ✅",
    "cancelled": "Отменен ❌"
}


# --- Конфигурация FSM (создание заявки) ---

# 1. Определяем услуги, их названия и возможные подуслуги.
FSM_SERVICES: dict[str, dict] = {
    'service_person_check': {
        'name': '👤 Проверка физического лица',
        # Если у услуги есть подуслуги, добавляем словарь 'sub_services'
        'sub_services': {
            'sub_basic_dossier': '📄 Базовое досье (от 15 000 руб.)',
            'sub_advanced_dossier': '📑 Продвинутое досье (от 30 000 руб.)',
            'sub_full_dossier': '📁 Полное досье (50 000 руб.)',
            'sub_consultation_needed': '❓Не знаю, нужна консультация',
        }
    },
    'service_due_diligence': {
        'name': '👥 Проверка контрагента',
        # У этой услуги нет подуслуг, поэтому она сразу перейдет к вопросам.
    },
    'service_private_investigation': {
        'name': '🔎 Частное расследование',
    },
    'service_other': {
        'name': '[Другое]',
    }
}

# 2. Определяем вопросы.
# Ключи ДОЛЖНЫ совпадать с ключами услуг из FSM_SERVICES (если нет подуслуг)
# или с ключами подуслуг (если они есть).
FSM_QUESTIONS: dict[str, list[dict[str, str]]] = {
    # Вопросы для подуслуг 'Проверки физического лица'
    'sub_basic_dossier': [
        {'key': 'whos_target', 'text': 'Вопрос 1: О ком или о чем необходимо собрать информацию (без конкретных имён)?'},
        {'key': 'objective', 'text': 'Вопрос 2: Какова основная цель обращения?'},
        {'key': 'current_info', 'text': 'Вопрос 3: Какая информация об объекте уже есть у вас?'},
        {'key': 'budget_timeline', 'text': 'Вопрос 4: Есть ли у вас бюджет и сроки?'},
        {'key': 'contact_info', 'text': 'Вопрос 5: Где с вами можно связаться? По умолчанию мы связываемся в Telegram с которого вы пишите (если у вас установлен username). Можете оставить иной TG или Email.'},
    ],
    'sub_advanced_dossier': [
        {'key': 'whos_target', 'text': 'Вопрос 1: О ком или о чем необходимо собрать информацию (без конкретных имён)?'},
        {'key': 'objective', 'text': 'Вопрос 2: Какова основная цель обращения?'},
        {'key': 'current_info', 'text': 'Вопрос 3: Какая информация об объекте (или его семье) уже есть у вас?'},
        {'key': 'budget_timeline', 'text': 'Вопрос 4: Есть ли у вас бюджет и сроки?'},
        {'key': 'contact_info', 'text': 'Вопрос 5: Где с вами можно связаться? По умолчанию мы связываемся в Telegram с которого вы пишите (если у вас установлен username). Можете оставить иной TG или Email.'},
    ],
    'sub_full_dossier': [
        {'key': 'whos_target', 'text': 'Вопрос 1: О ком или о чем необходимо собрать информацию (без конкретных имён)?'},
        {'key': 'objective', 'text': 'Вопрос 2: Какова основная цель обращения?'},
        {'key': 'current_info', 'text': 'Вопрос 3: Какая информация об объекте (или его семье, партнерах) уже есть у вас?'},
        {'key': 'budget_timeline', 'text': 'Вопрос 4: Есть ли у вас бюджет и сроки?'},
        {'key': 'contact_info', 'text': 'Вопрос 5: Где с вами можно связаться? По умолчанию мы связываемся в Telegram с которого вы пишите (если у вас установлен username). Можете оставить иной TG или Email.'},
    ],
    'sub_consultation_needed': [
        {'key': 'contact_info', 'text': 'Оставьте ваш контакт для связи, и мы вам поможем.'},
    ],

    # Вопросы для услуги 'Due Diligence' (без подуслуг)
    'service_due_diligence': [
        {'key': 'company_name', 'text': 'Вопрос 1: Кого вы хотите проверить? (Партнёр, контрагент, конкурент и т.д.).'},
        {'key': 'company_details', 'text': 'Вопрос 2: Что вам известно о человеке? (Без конкретной информации)'},
        {'key': 'check_purpose', 'text': 'Вопрос 3: Какова цель проверки?'},
    ],
    # Вопросы для услуги 'Частное расследование'
    'service_private_investigation': [
        {'key': 'situation_description', 'text': 'Вопрос 1: Опишите ситуацию, можно без обличающих подробностей.'},
        {'key': 'main_goal', 'text': 'Вопрос 2: Какова главная цель расследования?'},
    ],
    # Вопросы для услуги 'Другое'
    'service_other': [
        {'key': 'task_description', 'text': 'Вопрос 1: Опишите вашу задачу подробно.'},
    ]
}
# -----------------------------------------


# Тексты сообщений бота
LEXICON: dict[str, str] = {
    # Главное меню
    "main_menu_text": (
        "🏛️ *Главное меню*\n\nПриветствуем в боте-поддержке агентства *Santa Muerte*.\nЗдесь вы можете посмотреть файлы по вашим старым заказам, а также сделать новую заявку на заказ.\n\n"
        "🆔 ID: `{user_id}`\n"
        "📦 Заказов создано: `{orders_count}`\n"
        "🌟 Статус: *{role}*"
    ),
    "sub_service_prompt": "Выберите интересующую вас услугу.",

    # Реферальная программа
    "referral_link_text": (
        "🤝 Реферальная программа\n\n"
        "Ваша уникальная ссылка (нажмите, чтобы скопировать):\n"
        "`{referral_link}`"
    ),
    "new_referral_notification": "🎉 У вас новый реферал: {new_referral_info}",
    "my_referrals_title": "📊 Ваши рефералы:",
    "no_referrals_yet": "У вас пока нет рефералов.",

    # Мои заказы
    "my_cases_title": "📦 Список ваших заказов:",
    "my_cases_placeholder": "Здесь будут все ваши заказы. В будущем здесь появятся кнопки, например:\n 'Заказ #123 🔄 В работе'.",

    # FSM (Создание заявки)
    "fsm_cancel": "Действие отменено. Введите /menu для возврата.",
    "fsm_start_prompt": "Укажите, пожалуйста, основную цель вашего обращения.",
    "fsm_finish": "✅ Спасибо! Ваша заявка #{order_id} принята. Мы скоро с вами свяжемся. Введите /menu для возврата.",

    # Шаблон уведомления о новой заявке
    "new_application_header": "✅ *Новая заявка!* ID: `{order_id}`",
    "new_application_client": "👤 *Клиент:* {user_info}",
    "new_application_service": "▶️ *Услуга:* {service_category}",
    "new_application_sub_service": "➡️ *Подуслуга:* {sub_service_category}",


    # Админ-панель
    "admin_menu_title": "🛠️ Админ. опции",
    "admin_only_main_can_grant": "Только Главный администратор может выдавать права.",
    "admin_list_users_title": "👥 Список пользователей (Всего: {count}):\n\n",
    "admin_grant_prompt": "Введите ID пользователя, которому хотите выдать права администратора:",
    "admin_grant_success": "✅ Пользователю {user_id} успешно выданы права администратора.",
    "admin_grant_invalid_id": "❌ Некорректный ID. Пожалуйста, введите число.",
    "admin_user_not_found": "❌ Пользователь с ID {user_id} не найден в базе данных.",

    # --- Управление заказами (Админка) ---
    "admin_all_orders_title": "📦 Все заказы (Фильтр: {filter})",
    "admin_no_orders_found": "Заказы с таким статусом не найдены.",
    "admin_orders_list_prompt": "Для управления заказом, отправьте его ID (например, <code>A4T7B1</code>) или порядковый номер из списка (например, <code>2</code>).",
    "admin_order_not_found": "❌ Заказ с ID <code>{order_id}</code> не найден.",
    "admin_order_select_prompt": "Выберите действие для заказа <code>{order_id}</code>:",
    "admin_order_details": (
        "📝 <b>Детали заказа <code>{order_id}</code></b>\n\n"
        "<b>Название:</b> {name}\n"
        "<b>Статус:</b> {status}\n"
        "<b>Клиент:</b> {user_info}\n"
        "<b>Услуга:</b> {service}\n"
        "<b>Подуслуга:</b> {sub_service}\n"
        "--------------------\n"
        "{questions_answers}"
    ),
    "admin_change_status_prompt": "Выберите новый статус для заказа <code>{order_id}</code>:",
    "admin_status_updated": "✅ Статус заказа '<code>{order_id}</code>' изменен на '<b>{status}</b>'. Клиент уведомлен.",
    "notification_status_changed": "🔔 Статус вашего заказа <code>{order_id}</code> изменен на: <b>{status}</b>.",
    "admin_set_name_prompt": "Введите новое название для заказа <code>{order_id}</code>:",
    "admin_name_updated": "✅ Название заказа <code>{order_id}</code> изменено. Клиент уведомлен.",
    "notification_name_changed": "🔔 Вашему заказу <code>{order_id}</code> присвоено название: <b>{name}</b>.",

    # Внешние ссылки
    "faq_url": "https://telegra.ph/FAQ-Example-09-16",
    "channel_url": "https://t.me/telegram",
}

# Названия кнопок
BUTTONS: dict[str, str] = {
    "referral_program": "Реферальная программа 🤝",
    "my_cases": "Мои заказы 📦",
    "create_task": "Создать заявку 📝",
    "faq": "F.A.Q. ❓",
    "channel": "Наш канал 📢",
    "admin_options": "Админ. опции 🛠️",
    "back": "⬅️ Назад",
    "back_to_main_menu": "⬅️ В главное меню",
    "back_to_admin_menu": "⬅️ В админ-меню",
    "my_referrals": "Мои рефералы 📊",
    "admin_list_users": "Список пользователей 👥",
    "admin_all_orders": "Все заказы 📦",
    "admin_grant": "Выдать админку 🛠️",
    "next_page": "Вперед ➡️",
    "prev_page": "⬅️ Назад",
    "filter_all": "Все",
    "change_status": "Изменить статус ✏️",
    "set_name": "Задать название 📝",
    "back_to_orders_list": "⬅️ К списку заказов",

}
