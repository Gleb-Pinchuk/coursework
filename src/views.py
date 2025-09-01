from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd

from src.utils import (
    get_greeting,
    get_cards_info,
    get_top_transactions,
    get_currency_rates,
    get_stock_prices,
    get_events,
)


def main_page(datetime_str: str, df: pd.DataFrame, settings: dict[str, Any]) -> dict[str, Any]:
    """
    Страница «Главная».
    Принимает строку с датой и временем формата YYYY-MM-DD HH:MM:SS.
    Возвращает JSON с приветствием, картами, транзакциями, курсами валют и акциями.
    """
    try:
        current_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

        return {
            "greeting": get_greeting(current_time),
            "cards": get_cards_info(df),
            "top_transactions": get_top_transactions(df),
            "currency_rates": get_currency_rates(settings.get("currencies", [])),
            "stock_prices": get_stock_prices(settings.get("stocks", [])),
        }
    except Exception:
        logging.exception("Ошибка при формировании страницы 'Главная'")
        return {}


def events_page(date_str: str, df: pd.DataFrame, settings: dict[str, Any], period: str = "M") -> dict[str, Any]:
    """
    Страница «События».
    Принимает строку с датой (YYYY-MM-DD), DataFrame и настройки.
    Возвращает JSON с событиями за указанный период.
    """
    try:
        start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return get_events(df, start_date, period)
    except Exception:
        logging.exception("Ошибка при формировании страницы 'События'")
        return {}
