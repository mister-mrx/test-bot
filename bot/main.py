import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from bot.config import config
from bot.handlers import user_handlers, admin_handlers, fsm_handlers
# Импортируем наш новый middleware
from bot.middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Глобальный обработчик ошибок
async def on_error(event: ErrorEvent, bot: Bot):
    logger.error(f"Unhandled exception: {event.exception}", exc_info=True)
    # Можно добавить уведомление администратору о критической ошибке
    # await bot.send_message(config.MAIN_ADMIN_ID, "Произошла критическая ошибка в боте!")

async def main():
    logger.info("Starting bot...")

    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем глобальный обработчик ошибок
    dp.errors.register(on_error, F.exception)

    # Регистрируем middleware для защиты от флуда на все сообщения
    dp.message.middleware(ThrottlingMiddleware())

    dp.include_router(fsm_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped manually")
