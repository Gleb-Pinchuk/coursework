import logging
import re
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)


def cashback_categories(year: int, month: int, transactions: List[Dict[str, Any]]) -> dict:
    total = sum(tx.get("amount", 0) for tx in transactions)
    cashback = round(total * 0.01, 2)
    return {
        "report": "cashback_service",
        "year": year,
        "month": month,
        "summary": {"cashback": cashback},
    }


def invest_piggybank(percent: float, transactions: List[Dict[str, Any]], min_amount: int) -> dict:
    savings = sum(
        tx["amount"] * percent / 100
        for tx in transactions
        if tx["amount"] >= min_amount
    )
    return {
        "report": "invest_piggybank",
        "savings": round(savings, 2),
    }


def simple_search(keyword: str, transactions: List[Dict[str, Any]]) -> dict:
    results = [tx for tx in transactions if keyword.lower() in tx.get("desc", "").lower()]
    return {"matches": results}


def phone_search(transactions: List[Dict[str, Any]]) -> dict:
    pattern = re.compile(r"\+7\d{10}")
    results = [tx for tx in transactions if pattern.search(tx.get("desc", ""))]
    return {"matches": results}


def p2p_search(transactions: List[Dict[str, Any]]) -> dict:
    pattern = re.compile(r"Перевод\s+\w+")
    results = [tx for tx in transactions if pattern.search(tx.get("desc", ""))]
    return {"matches": results}
