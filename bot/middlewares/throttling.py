from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache

# Используем TTLCache для хранения истории запросов с временем жизни (TTL)
# Ключ - user_id, значение - количество запросов
# cachetools - легковесная библиотека, добавьте ее в requirements.txt
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.7):
        # rate_limit - минимально допустимый интервал между сообщениями (в секундах)
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # Проверяем, есть ли пользователь в кеше
        if event.chat.id in self.cache:
            # Если есть, значит, он отправляет сообщения слишком часто
            # Игнорируем это сообщение и не передаем его дальше
            return

        # Если пользователя нет в кеше, добавляем его
        self.cache[event.chat.id] = None

        # Передаем управление следующему обработчику
        return await handler(event, data)
