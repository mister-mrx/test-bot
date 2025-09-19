import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
# Для использования RedisStorage в будущем, раскомментируйте строки ниже:
# from aiogram.fsm.storage.redis import RedisStorage

from bot.config import config
# Импортируем роутеры из разных модулей
from bot.handlers import user_handlers, admin_handlers, fsm_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting bot...")

    # Инициализация бота
    # Мы не устанавливаем parse_mode по умолчанию, а указываем его явно в хэндлерах (Markdown или HTML)
    bot = Bot(token=config.BOT_TOKEN)

    # Инициализация хранилища
    # Используем MemoryStorage (данные хранятся в памяти и теряются при перезапуске)
    storage = MemoryStorage()

    # TODO: Для продакшена замените MemoryStorage на RedisStorage
    # storage = RedisStorage.from_url("redis://localhost:6379/0")

    # Инициализация диспетчера
    dp = Dispatcher(storage=storage)

    # Подключение роутеров. Порядок важен!
    # Роутер FSM (для обработки состояний и команды /cancel)
    dp.include_router(fsm_handlers.router)
    # Админский роутер (с фильтрами прав доступа)
    dp.include_router(admin_handlers.router)
    # Пользовательский роутер (для всех остальных команд)
    dp.include_router(user_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    # Передаем объект bot в диспетчер, чтобы он был доступен в хэндлерах (например, для генерации реф. ссылок или отправки уведомлений)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped manually")