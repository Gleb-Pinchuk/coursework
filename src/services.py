import os
import logging
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def get_currency_rates(currencies: List[str]) -> Dict[str, Any]:
    """Получает актуальные курсы валют по отношению к рублю."""
    api_key = os.getenv("CURRENCY_API_KEY")
    base_url = os.getenv("CURRENCY_BASE_URL", "https://api.currencyprovider.com/latest")

    if not api_key:
        return {"success": False, "error": "Currency API key not configured"}

    if not currencies:
        return {"success": False, "error": "No currencies specified"}

    try:
        params = {
            "apikey": api_key,
            "base_currency": "RUB",
            "currencies": ",".join(currencies)
        }

        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            rates = {
                cur: data["data"][cur]["value"]
                for cur in currencies
                if cur in data.get("data", {})
            }
            return {"success": True, "data": rates}
        else:
            error_msg = data.get("error", {}).get("message", "Unknown API error")
            return {"success": False, "error": error_msg}

    except requests.exceptions.RequestException as e:
        logger.error("Network error in currency API: %s", e)
        return {"success": False, "error": f"Network error: {e}"}

    except ValueError as e:
        logger.error("JSON parse error in currency API: %s", e)
        return {"success": False, "error": f"JSON parse error: {e}"}


def get_stock_prices(stocks: List[str]) -> Dict[str, Any]:
    """Получает актуальные цены акций."""
    api_key = os.getenv("STOCKS_API_KEY")
    base_url = os.getenv("STOCKS_BASE_URL", "https://api.stocksprovider.com/query")

    if not api_key:
        return {"success": False, "error": "Stocks API key not configured"}

    if not stocks:
        return {"success": False, "error": "No stocks specified"}

    result = {"success": True, "data": {}}

    for stock in stocks:
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": stock,
                "apikey": api_key
            }

            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            quote = data.get("Global Quote", {})
            price = quote.get("05. price")

            if price is not None:
                result["data"][stock] = float(price)
            else:
                result["success"] = False
                result["error"] = f"No price for {stock}"

        except requests.exceptions.RequestException as e:
            logger.error("Network error for stock %s: %s", stock, e)
            result["success"] = False
            result["error"] = f"Network error for {stock}: {e}"

        except ValueError as e:
            logger.error("JSON parse error for stock %s: %s", stock, e)
            result["success"] = False
            result["error"] = f"JSON parse error for {stock}: {e}"

    return result


def get_financial_data(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Получает данные о валютах и акциях на основе пользовательских настроек."""
    currencies = settings.get("currencies", [])
    stocks = settings.get("stocks", [])

    result = {"currencies": {}, "stocks": {}}

    if currencies:
        currency_data = get_currency_rates(currencies)
        if currency_data.get("success"):
            result["currencies"] = currency_data["data"]

    if stocks:
        stocks_data = get_stock_prices(stocks)
        if stocks_data.get("success"):
            result["stocks"] = stocks_data["data"]

    return result
