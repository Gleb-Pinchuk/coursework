import json
import logging
from pathlib import Path
from typing import Any, NoReturn
import os

from src.utils import load_operations
from src.views import events_page, main_page
from src.services import get_financial_data

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
    Загружает пользовательские настройки из файла user_settings.json.
    """
    settings_path = BASE_DIR / "user_settings.json"
    try:
        with open(settings_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("Файл настроек '%s' не найден. Будет использован пустой набор настроек.", settings_path)
        return {}
    except json.JSONDecodeError as e:
        logging.error("Ошибка декодирования JSON в файле '%s': %s", settings_path, e)
        return {}


def critical_error_exit(message: str) -> NoReturn:
    """
    Логирует критическую ошибку и завершает работу приложения.
    """
    logging.critical(message)
    exit(1)


def run() -> None:
    """
    Главная точка запуска проекта.
    """
    try:
        logging.info("Загрузка транзакций...")
        data_file_path = BASE_DIR / "data" / "operations.xlsx"
        if not data_file_path.exists():
            critical_error_exit(f"Файл с данными не найден: {data_file_path}")

        df = load_operations(data_file_path)
        if df is None or df.empty:
            critical_error_exit("Не удалось загрузить данные транзакций или DataFrame пуст.")

        logging.info("Загрузка настроек пользователя...")
        settings: dict[str, Any] = load_user_settings()

        logging.info("Получение данных о валютах и акциях...")
        financial_data = get_financial_data(settings)
        logging.info("Данные о финансах получены: %s",
                     {k: len(v) for k, v in financial_data.items()})

        logging.info("Формирование главной страницы...")
        homepage_json: dict[str, Any] = main_page(
            "2020-05-20 15:45:00", df, settings, financial_data
        )
        print(json.dumps(homepage_json, indent=4, ensure_ascii=False))

        logging.info("Формирование страницы событий...")
        events_json: dict[str, Any] = events_page(
            "2020-05-20", df, settings, period="M"
        )
        print(json.dumps(events_json, indent=4, ensure_ascii=False))

    except Exception as error:
        logging.error("Непредвиденная ошибка при запуске: %s", error, exc_info=True)
        critical_error_exit("Приложение остановлено из-за непредвиденной ошибки.")


if __name__ == "__main__":
    run()
