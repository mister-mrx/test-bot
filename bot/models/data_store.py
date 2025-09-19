from typing import Optional, Any
from math import ceil
import random
import string
from bot.config import config

# Временные хранилища данных в памяти
# TODO: Replace with DB logic (e.g., SQLAlchemy/TortoiseORM models)

# Структура пользователя: {user_id: {"username": str, "role": str, "referrer_id": int}}
users_db: dict[int, dict[str, Any]] = {}
# Структура заказа: {order_id: {"user_id": int, "status": str, "details": dict}}
orders_db: dict[str, dict[str, Any]] = {}


# --- Функции управления данными (Имитация запросов к БД) ---

def generate_unique_order_id(length: int = 6) -> str:
    """Генерирует уникальный 6-значный ID для заказа."""
    while True:
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if order_id not in orders_db:
            return order_id

def register_user(user_id: int, username: Optional[str], referrer_id: Optional[int] = None) -> int | None:
    """
    Регистрирует нового пользователя.
    Возвращает ID реферера, если пользователь новый и пришел по ссылке.
    """
    assigned_referrer_id = None
    if user_id not in users_db:
        # Определяем роль. Если это главный админ, присваиваем соответствующую роль.
        role = "main_admin" if user_id == config.MAIN_ADMIN_ID else "client"

        # Убедимся, что пользователь не является своим же рефералом
        if referrer_id and referrer_id != user_id:
            assigned_referrer_id = referrer_id

        users_db[user_id] = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "referrer_id": assigned_referrer_id
        }
        return assigned_referrer_id

    # Обновляем username, если он изменился
    users_db[user_id]["username"] = username
    # Убедимся, что роль главного админа актуальна (важно при перезапуске MemoryStorage)
    if user_id == config.MAIN_ADMIN_ID and users_db[user_id]["role"] != "main_admin":
        users_db[user_id]["role"] = "main_admin"
    return None

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

def add_order(user_id: int, details: dict) -> str:
    """Добавляет новый заказ с уникальным ID."""
    order_id = generate_unique_order_id()
    orders_db[order_id] = {
        "order_id": order_id,
        "user_id": user_id,
        "status": "Новый", # Статус по умолчанию
        "details": details
    }
    return order_id

def get_user_orders(user_id: int, page: int = 1, page_size: int = 3) -> tuple[list, int]:
    """Получает список заказов пользователя с пагинацией."""
    user_orders = sorted(
        [order for order in orders_db.values() if order["user_id"] == user_id],
        key=lambda x: x['order_id']
    )
    
    total_items = len(user_orders)
    if total_items == 0:
        return [], 0
        
    total_pages = ceil(total_items / page_size)
    
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    return user_orders[start_index:end_index], total_pages


def get_referrals(user_id: int, page: int = 1, page_size: int = 10) -> tuple[list, int]:
    """Получает список рефералов пользователя с пагинацией."""
    referrals = [user for user in users_db.values() if user.get("referrer_id") == user_id]
    
    total_items = len(referrals)
    if total_items == 0:
        return [], 0

    total_pages = ceil(total_items / page_size)

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    return referrals[start_index:end_index], total_pages


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
