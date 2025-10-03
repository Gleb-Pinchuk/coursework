import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def load_operations(file_path: str) -> Optional[pd.DataFrame]:
    """
    Загружает данные об операциях из Excel файла.
    """
    try:
        logger.info("Загрузка операций из файла: %s", file_path)
        df = pd.read_excel(file_path)

        required_columns = ['Дата операции', 'Сумма операции']
        for col in required_columns:
            if col not in df.columns:
                logger.error("Отсутствует обязательная колонка: %s", col)
                return None

        df['Дата операции'] = pd.to_datetime(df['Дата операции'])

        logger.info("Успешно загружено %d операций", len(df))
        return df

    except FileNotFoundError:
        logger.error("Файл не найден: %s", file_path)
        return None
    except Exception as e:
        logger.error("Ошибка загрузки файла %s: %s", file_path, e)
        return None


def format_currency(amount: float, currency: str = "RUB") -> str:
    """
    Форматирует денежную сумму с указанием валюты.
    """
    try:
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        else:
            return f"{amount:,.2f} ₽"
    except Exception as e:
        logger.error("Ошибка форматирования валюты: %s", e)
        return str(amount)
