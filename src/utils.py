from __future__ import annotations

import json
import logging
from datetime import datetime, date
from typing import Any

import pandas as pd
import requests


def read_transactions_excel(file_path: str) -> pd.DataFrame:
    """
    Читает Excel-файл с транзакциями и приводит его к единому формату.
    """
    df = pd.read_excel(file_path, parse_dates=["Дата операции"])

    df = df.rename(
        columns={
            "Дата операции": "date",
            "Номер карты": "card",
            "Сумма операции": "amount",
            "Категория": "category",
            "Описание": "description",
            "Валюта операции": "currency",
        }
    )

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["card"] = df["card"].astype(str).str.strip()

    df = df.dropna(subset=["amount"])

    return df


# ---------- Главная ----------

def get_greeting(current_time: datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.
    """
    hour = current_time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    if 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def get_cards_info(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Возвращает список карт с балансами.
    Баланс считается как сумма операций по каждой карте.
    """
    cards = (
        df.groupby("card")["amount"].sum().reset_index().sort_values(by="card")
    )
    return [
        {"card": row["card"], "balance": round(row["amount"], 2)}
        for _, row in cards.iterrows()
    ]


def get_top_transactions(df: pd.DataFrame, n: int = 5) -> list[dict[str, Any]]:
    """
    Возвращает топ-N транзакций по абсолютной сумме.
    """
    top = df.loc[df["amount"].abs().nlargest(n).index]
    return [
        {
            "date": row["date"].strftime("%Y-%m-%d %H:%M:%S"),
            "amount": round(row["amount"], 2),
            "category": row["category"],
            "description": row["description"],
        }
        for _, row in top.iterrows()
    ]


def get_currency_rates(currencies: list[str]) -> dict[str, float]:
    """
    Загружает курсы валют с внешнего API.
    """
    rates: dict[str, float] = {}
    try:
        response = requests.get("https://api.exchangerate.host/latest?base=RUB", timeout=10)
        data = response.json()
        for cur in currencies:
            if cur in data["rates"]:
                rates[cur] = round(data["rates"][cur], 2)
    except Exception:
        logging.exception("Ошибка при загрузке курсов валют")
    return rates


def get_stock_prices(stocks: list[str]) -> dict[str, float]:
    """
    Загружает цены акций (заглушка).
    В реальном проекте можно подключить API (например, Yahoo Finance).
    """
    prices: dict[str, float] = {}
    try:
        for stock in stocks:
            # Здесь вместо API — заглушка
            prices[stock] = 100.0
    except Exception:
        logging.exception("Ошибка при загрузке цен акций")
    return prices


# ---------- События ----------

def get_events(df: pd.DataFrame, start_date: date, period: str = "M") -> dict[str, Any]:
    """
    Группирует события (транзакции) по периоду (день/неделя/месяц).
    """
    try:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])

        if period == "D":
            df["period"] = df["date"].dt.date
        elif period == "W":
            df["period"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time.date())
        else:
            df["period"] = df["date"].dt.to_period("M").apply(lambda r: r.start_time.date())

        grouped = df.groupby("period").agg(
            total_amount=("amount", "sum"),
            transaction_count=("amount", "count"),
        ).reset_index()

        return {
            "start_date": str(start_date),
            "period": period,
            "events": [
                {
                    "period": str(row["period"]),
                    "total_amount": round(row["total_amount"], 2),
                    "transaction_count": int(row["transaction_count"]),
                }
                for _, row in grouped.iterrows()
            ],
        }
    except Exception:
        logging.exception("Ошибка при формировании событий")
        return {}
