import json
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.utils import read_transactions_excel
from src.views import events_page, main_page

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
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
        df = read_transactions_excel(BASE_DIR / "data" / "operations.xlsx")

        logging.info("Загрузка настроек пользователя...")
        settings = load_user_settings()

        logging.info("Формирование главной страницы...")
        homepage_json = main_page("2020-05-20 15:45:00", df, settings)
        print(json.dumps(homepage_json, indent=4, ensure_ascii=False))

        logging.info("Формирование страницы событий...")
        events_json = events_page("2020-05-20", df, settings, period="M")
        print(json.dumps(events_json, indent=4, ensure_ascii=False))

    except Exception:
        logging.exception("Ошибка при запуске")


if __name__ == "__main__":
    run()
