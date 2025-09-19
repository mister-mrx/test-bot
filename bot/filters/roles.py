from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from bot.models.data_store import get_user_role

class IsAdmin(Filter):
    """
    Фильтр проверяет, является ли пользователь администратором
    ИЛИ главным администратором.
    """
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        role = get_user_role(user_id)
        return role in ["admin", "main_admin"]

class IsMainAdmin(Filter):
    """
    Фильтр проверяет, является ли пользователь ГЛАВНЫМ администратором.
    """
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        role = get_user_role(user_id)
        # Проверка основана на данных из data_store, которые синхронизируются с MAIN_ADMIN_ID
        return role == "main_admin"