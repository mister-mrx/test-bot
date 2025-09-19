import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Загружаем переменные из файла .env
load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str
    MAIN_ADMIN_ID: int

# Функция для загрузки и валидации конфигурации
def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    admin_id_str = os.getenv("MAIN_ADMIN_ID")

    if not token or not admin_id_str:
        raise ValueError("Не все переменные окружения установлены (.env: BOT_TOKEN, MAIN_ADMIN_ID)")

    try:
        admin_id = int(admin_id_str)
    except ValueError:
        raise ValueError("MAIN_ADMIN_ID должен быть числом")

    return Config(
        BOT_TOKEN=token,
        MAIN_ADMIN_ID=admin_id,
    )

# Глобальная переменная конфигурации
config = load_config()