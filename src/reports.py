import json
import logging
from datetime import datetime
from typing import Optional, Callable

import pandas as pd

logging.basicConfig(level=logging.INFO)


def report_decorator(filename: Optional[str] = None):
    """
    Декоратор для сохранения результата отчёта в JSON-файл.
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            file = filename or f"report_{func.__name__}.json"
            with open(file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            logging.info("Report %s written to %s", func.__name__, file)
            return result
        return wrapper
    return decorator


@report_decorator()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> dict:
    """
    Возвращает траты по категории за последние 3 месяца.
    """
    if date is None:
        date = datetime.today()
    else:
        date = pd.to_datetime(date)

    start_date = date - pd.DateOffset(months=3)
    filtered = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= date)
        & (transactions["Категория"] == category)
    ]

    total = float(filtered["Сумма операции"].sum())
    return {"report": "spending_by_category", "data": {"category": category, "total": total}}


@report_decorator()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> dict:
    """
    Возвращает средние траты по дням недели за последние 3 месяца.
    """
    if date is None:
        date = datetime.today()
    else:
        date = pd.to_datetime(date)

    start_date = date - pd.DateOffset(months=3)
    filtered = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= date)
    ].copy()

    filtered["weekday"] = filtered["Дата операции"].dt.day_name()
    result = filtered.groupby("weekday")["Сумма операции"].mean().to_dict()
    return {"report": "spending_by_weekday", "data": {k: float(v) for k, v in result.items()}}


@report_decorator()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> dict:
    """
    Возвращает средние траты в рабочие и выходные дни за последние 3 месяца.
    """
    if date is None:
        date = datetime.today()
    else:
        date = pd.to_datetime(date)

    start_date = date - pd.DateOffset(months=3)
    filtered = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= date)
    ].copy()

    filtered["is_workday"] = filtered["Дата операции"].dt.weekday < 5
    result = filtered.groupby("is_workday")["Сумма операции"].mean().to_dict()

    return {
        "report": "spending_by_workday",
        "data": {
            "workday": float(result.get(True, 0)),
            "weekend": float(result.get(False, 0)),
        },
    }
