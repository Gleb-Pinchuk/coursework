import os
import logging
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCKS_API_KEY = os.getenv("STOCKS_API_KEY")


def get_currency_rates(currencies: List[str]) -> Dict[str, Any]:
    """
    Получает актуальные курсы валют по отношению к рублю.
    """
    if not CURRENCY_API_KEY:
        logger.error("Не задан CURRENCY_API_KEY")
        return {"success": False, "error": "Currency API key not configured"}

    if not currencies:
        logger.error("Не задан список валют")
        return {"success": False, "error": "No currencies specified"}

    try:
        params = {
            "apikey": CURRENCY_API_KEY,
            "base_currency": "RUB",
            "currencies": ",".join(currencies)
        }

        logger.info("Запрос курсов валют: %s", currencies)
        response = requests.get(CURRENCY_BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("success", False):
            rates = {}
            for currency in currencies:
                rate = data.get("data", {}).get(currency, {}).get("value")
                if rate:
                    rates[currency] = rate

            logger.info("Успешно получены курсы для %d валют", len(rates))
            return {"success": True, "data": rates}
        else:
            error_msg = data.get("error", {}).get("message", "Unknown API error")
            logger.error("Ошибка API валют: %s", error_msg)
            return {"success": False, "error": error_msg}

    except requests.exceptions.RequestException as e:
        logger.error("Ошибка сети при запросе курсов валют: %s", e)
        return {"success": False, "error": f"Network error: {e}"}
    except ValueError as e:
        logger.error("Ошибка парсинга JSON: %s", e)
        return {"success": False, "error": f"JSON parse error: {e}"}


def get_stock_prices(stocks: List[str]) -> Dict[str, Any]:
    """
    Получает актуальные цены акций.
    """
    if not STOCKS_API_KEY:
        logger.error("Не задан STOCKS_API_KEY")
        return {"success": False, "error": "Stocks API key not configured"}

    if not stocks:
        logger.error("Не задан список акций")
        return {"success": False, "error": "No stocks specified"}

    results = {"success": True, "data": {}}

    for stock in stocks:
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": stock,
                "apikey": STOCKS_API_KEY
            }

            logger.info("Запрос цены акции: %s", stock)
            response = requests.get(STOCKS_BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            quote = data.get("Global Quote", {})

            if quote:
                price = quote.get("05. price")
                if price:
                    results["data"][stock] = float(price)
                    logger.info("Получена цена для %s: %s", stock, price)
                else:
                    logger.warning("Не удалось получить цену для %s", stock)
            else:
                logger.warning("Некорректный ответ API для %s", stock)

        except requests.exceptions.RequestException as e:
            logger.error("Ошибка сети для %s: %s", stock, e)
            results["success"] = False
            results["error"] = f"Network error for {stock}: {e}"
        except ValueError as e:
            logger.error("Ошибка парсинга JSON для %s: %s", stock, e)
            results["success"] = False
            results["error"] = f"JSON parse error for {stock}: {e}"

    return results


def get_financial_data(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Получает данные о валютах и акциях на основе пользовательских настроек.
    """
    currencies = settings.get("currencies", [])
    stocks = settings.get("stocks", [])

    result = {
        "currencies": {},
        "stocks": {}
    }

    if currencies:
        currency_data = get_currency_rates(currencies)
        if currency_data.get("success"):
            result["currencies"] = currency_data["data"]
        else:
            logger.warning("Не удалось получить данные о валютах: %s",
                           currency_data.get("error", "Unknown error"))

    if stocks:
        stocks_data = get_stock_prices(stocks)
        if stocks_data.get("success"):
            result["stocks"] = stocks_data["data"]
        else:
            logger.warning("Не удалось получить данные об акциях: %s",
                           stocks_data.get("error", "Unknown error"))

    return result
