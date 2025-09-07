import json
import logging
from pathlib import Path
from typing import Any
from src.utils import load_operations
from src.views import events_page, main_page
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

BASE_DIR = Path(__file__).resolve().parent.parent


def load_user_settings() -> dict[str, Any]:
    """
    Загружает пользовательские настройки (валюты и акции).
    """
    settings_path = BASE_DIR / "user_settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run() -> None:
    """
    Главная точка запуска проекта.
    """
    try:
        logging.info("Загрузка транзакций...")
        df = load_operations(BASE_DIR / "data" / "operations.xlsx")

        logging.info("Загрузка настроек пользователя...")
        settings: dict[str, Any] = load_user_settings()

        logging.info("Формирование главной страницы...")
        homepage_json: dict[str, Any] = main_page(
            "2020-05-20 15:45:00", df, settings
        )
        print(json.dumps(homepage_json, indent=4, ensure_ascii=False))

        logging.info("Формирование страницы событий...")
        events_json: dict[str, Any] = events_page(
            "2020-05-20", df, settings, period="M"
        )
        print(json.dumps(events_json, indent=4, ensure_ascii=False))

    except Exception as e:
        logging.error("Ошибка при запуске: %s", e, exc_info=True)


if __name__ == "__main__":
    run()
