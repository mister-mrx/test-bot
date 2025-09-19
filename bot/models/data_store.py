from typing import Optional, Any
from bot.config import config

# Временные хранилища данных в памяти
# TODO: Replace with DB logic (e.g., SQLAlchemy/TortoiseORM models)

# Структура пользователя: {user_id: {"username": str, "role": str, "referrer_id": int}}
users_db: dict[int, dict[str, Any]] = {}
# Структура заказа: {order_id: {"user_id": int, "status": str, "details": dict}}
orders_db: dict[int, dict[str, Any]] = {}
order_counter = 0

# --- Функции управления данными (Имитация запросов к БД) ---

def register_user(user_id: int, username: Optional[str], referrer_id: Optional[int] = None) -> bool:
    """Регистрирует нового пользователя, если его еще нет в базе."""
    if user_id not in users_db:
        # Определяем роль. Если это главный админ, присваиваем соответствующую роль.
        role = "main_admin" if user_id == config.MAIN_ADMIN_ID else "client"

        # Убедимся, что пользователь не является своим же рефералом
        if referrer_id == user_id:
            referrer_id = None

        users_db[user_id] = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "referrer_id": referrer_id
        }
        return True
    # Обновляем username, если он изменился
    users_db[user_id]["username"] = username
    # Убедимся, что роль главного админа актуальна (важно при перезапуске MemoryStorage)
    if user_id == config.MAIN_ADMIN_ID and users_db[user_id]["role"] != "main_admin":
        users_db[user_id]["role"] = "main_admin"
    return False

def get_user_data(user_id: int) -> Optional[dict[str, Any]]:
    """Получает данные пользователя."""
    return users_db.get(user_id)

def get_user_role(user_id: int) -> str:
    """Получает ключ роли пользователя (client, admin, main_admin)."""
    user_data = get_user_data(user_id)
    return user_data.get("role", "client") if user_data else "client"

def get_orders_count(user_id: int) -> int:
    """Считает количество заказов пользователя."""
    # TODO: Replace with DB query (COUNT(*))
    return len([order for order in orders_db.values() if order["user_id"] == user_id])

def add_order(user_id: int, details: dict) -> int:
    """Добавляет новый заказ."""
    global order_counter
    order_counter += 1
    order_id = order_counter
    orders_db[order_id] = {
        "order_id": order_id,
        "user_id": user_id,
        "status": "new",
        "details": details
    }
    return order_id

def get_referrals(user_id: int) -> list[dict[str, Any]]:
    """Получает список рефералов пользователя."""
    # TODO: Replace with DB query (SELECT * WHERE referrer_id = ?)
    return [user for user in users_db.values() if user.get("referrer_id") == user_id]

def grant_admin_role(user_id: int) -> bool:
    """Выдает права администратора пользователю."""
    if user_id in users_db:
        # Нельзя изменить роль главного администратора
        if users_db[user_id]["role"] != "main_admin":
            users_db[user_id]["role"] = "admin"
            return True
    return False

def get_all_users() -> list[dict[str, Any]]:
    """Получает список всех пользователей."""
    return list(users_db.values())