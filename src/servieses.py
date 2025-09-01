from __future__ import annotations

import logging
import math
import re
from functools import reduce
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Union

import pandas as pd

logger = logging.getLogger(__name__)

Transaction = Mapping[str, Any]


def _to_list(transactions: Union[pd.DataFrame, Iterable[Transaction]]) -> List[Dict[str, Any]]:
    """
    Приводит входные транзакции к списку словарей.
    Поддерживается DataFrame (pandas) или уже список словарей.
    """
    if isinstance(transactions, pd.DataFrame):
        return transactions.to_dict(orient="records")
    return list(transactions)


def _get_tx_date(tx: Transaction):
    """
    Попытка распарсить дату транзакции из полей 'Дата операции' / 'date'.
    Возвращает pandas.Timestamp или None.
    """
    date_val = tx.get("Дата операции") or tx.get("date") or tx.get("Дата")
    if date_val is None:
        return None
    # pandas удобнее для разных форматов
    try:
        return pd.to_datetime(date_val, dayfirst=False, errors="coerce")
    except Exception:
        return None


# ------------------ 1) Выгодные категории повышенного кешбэка ------------------
def analyze_cashback_categories(transactions: Union[pd.DataFrame, Iterable[Transaction]],
                                year: int,
                                month: int) -> Dict[str, int]:
    """
    Анализ, сколько кешбэка (в рублях) можно было заработать по категориям за указанный месяц.
    Правило кешбэка: 1 рубль за каждые полные 100 рублей расходов (floor(abs(amount) / 100)).

    :param transactions: DataFrame или iterable словарей с транзакциями
    :param year: год (например, 2025)
    :param month: месяц (1-12)
    :return: словарь { "Категория": кешбэк (int) }
    """
    tx_list = _to_list(transactions)

    # Отфильтровать по месяцу и только расходы (amount < 0)
    def in_month_and_expense(tx: Transaction) -> bool:
        dt = _get_tx_date(tx)
        if pd.isna(dt) or dt is None:
            return False
        try:
            return (dt.year == int(year)) and (dt.month == int(month)) and (float(tx.get("Сумма операции", tx.get("amount", 0))) < 0)
        except Exception:
            return False

    filtered = list(filter(in_month_and_expense, tx_list))

    # map -> (category, cashback)
    def tx_to_pair(tx: Transaction):
        amt = float(tx.get("Сумма операции", tx.get("amount", 0)))
        cashback = int(abs(amt) // 100)  # 1 рубль за каждую полную 100 ₽
        category = tx.get("Категория") or tx.get("category") or "Неизвестно"
        return category, cashback

    pairs = map(tx_to_pair, filtered)

    # reduce -> суммируем по категориям
    def reducer(acc: MutableMapping[str, int], pair):
        cat, cb = pair
        acc[cat] = acc.get(cat, 0) + int(cb)
        return acc

    result: Dict[str, int] = reduce(reducer, pairs, {})
    # Отфильтруем нулевой кешбэк, если нужно — оставим только категории с >0
    result = {k: v for k, v in result.items() if v > 0}
    logger.info("Анализ кешбэка за %04d-%02d: найдено %d категорий", year, month, len(result))
    return result


# ------------------ 2) Инвесткопилка ------------------
def investment_bank(month: str, transactions: Union[pd.DataFrame, Iterable[Transaction]], limit: int) -> float:
    """
    Рассчитывает сумму отложений в "Инвесткопилку" — разница между округлённой вверх суммой и фактической тратой.
    :param month: 'YYYY-MM' например '2025-07'
    :param transactions: список транзакций (или DataFrame)
    :param limit: 10, 50 или 100 (шаг для округления)
    :return: отложенная сумма (float, две десятичные)
    """
    if limit <= 0:
        raise ValueError("limit must be positive")

    tx_list = _to_list(transactions)
    prefix = str(month)
    saved = 0.0

    def relevant(tx: Transaction) -> bool:
        dt = _get_tx_date(tx)
        if pd.isna(dt) or dt is None:
            return False
        # month match YYYY-MM
        try:
            return dt.strftime("%Y-%m") == prefix and float(tx.get("Сумма операции", tx.get("amount", 0))) < 0
        except Exception:
            return False

    for tx in filter(relevant, tx_list):
        amount = float(tx.get("Сумма операции", tx.get("amount", 0)))
        spend = abs(amount)
        rounded = math.ceil(spend / limit) * limit
        diff = rounded - spend
        saved += diff

    saved = round(saved, 2)
    logger.info("Investbank for %s with limit %d => saved %s", month, limit, saved)
    return saved


# ------------------ 3) Простой поиск ------------------
def simple_search(query: str, transactions: Union[pd.DataFrame, Iterable[Transaction]]) -> Dict[str, Any]:
    """
    Ищет транзакции, где query входит в описание или категорию (регистронезависимо).
    Возвращает JSON-подобную структуру.
    """
    q = str(query).strip().lower()
    tx_list = _to_list(transactions)

    def matches(tx: Transaction) -> bool:
        desc = str(tx.get("Описание", tx.get("description", ""))).lower()
        cat = str(tx.get("Категория", tx.get("category", ""))).lower()
        return q in desc or q in cat

    results = list(filter(matches, tx_list))
    logger.info("Simple search '%s' found %d results", query, len(results))
    return {"query": query, "count": len(results), "results": results}


# ------------------ 4) Поиск по телефонным номерам ------------------
_PHONE_RE = re.compile(r"(?:\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}")

def find_phone_numbers(transactions: Union[pd.DataFrame, Iterable[Transaction]]) -> Dict[str, Any]:
    tx_list = _to_list(transactions)

    def has_phone(tx: Transaction) -> bool:
        return bool(_PHONE_RE.search(str(tx.get("Описание", tx.get("description", "")))))

    results = list(filter(has_phone, tx_list))
    logger.info("Found %d transactions with phone numbers", len(results))
    return {"count": len(results), "results": results}


# ------------------ 5) Поиск переводов физическим лицам ------------------
# шаблон: "Имя X." (кириллица, имя с заглавной буквы, пробел, заглавная буква фамилии и точка)
_P2P_RE = re.compile(r"\b[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.\b")

def find_p2p_transfers(transactions: Union[pd.DataFrame, Iterable[Transaction]]) -> Dict[str, Any]:
    tx_list = _to_list(transactions)

    def is_p2p(tx: Transaction) -> bool:
        cat = str(tx.get("Категория", tx.get("category", ""))).strip()
        if cat != "Переводы":
            return False
        return bool(_P2P_RE.search(str(tx.get("Описание", tx.get("description", "")))))

    results = list(filter(is_p2p, tx_list))
    logger.info("Found %d P2P transfers", len(results))
    return {"count": len(results), "results": results}
