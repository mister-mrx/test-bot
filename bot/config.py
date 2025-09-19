import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Загружаем переменные из файла .env
load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str
    MAIN_ADMIN_ID: int
    GROUP_CHAT_ID: int | None # ID чата для уведомлений, может быть не указан

# Функция для загрузки и валидации конфигурации
def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    admin_id_str = os.getenv("MAIN_ADMIN_ID")
    group_chat_id_str = os.getenv("GROUP_CHAT_ID")

    if not token or not admin_id_str:
        raise ValueError("Не установлены обязательные переменные окружения (.env: BOT_TOKEN, MAIN_ADMIN_ID)")

    try:
        admin_id = int(admin_id_str)
    except ValueError:
        raise ValueError("MAIN_ADMIN_ID должен быть числом")

    group_chat_id = None
    if group_chat_id_str:
        try:
            group_chat_id = int(group_chat_id_str)
        except ValueError:
            raise ValueError("GROUP_CHAT_ID должен быть числом")


    return Config(
        BOT_TOKEN=token,
        MAIN_ADMIN_ID=admin_id,
        GROUP_CHAT_ID=group_chat_id
    )

# Глобальная переменная конфигурации
config = load_config()