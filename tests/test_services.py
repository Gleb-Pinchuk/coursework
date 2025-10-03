import os
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import pandas as pd

from src.services import get_currency_rates, get_stock_prices, get_financial_data


class TestServices(unittest.TestCase):
    """Тесты для сервисов получения финансовых данных."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.test_currencies = ["USD", "EUR"]
        self.test_stocks = ["AAPL", "GOOGL"]
        self.test_settings = {
            "currencies": self.test_currencies,
            "stocks": self.test_stocks
        }

    @patch.dict(os.environ, {"CURRENCY_API_KEY": "test_key"})
    @patch('src.services.requests.get')
    def test_get_currency_rates_success(self, mock_get):
        """Тест успешного получения курсов валют."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "USD": {"value": 75.50},
                "EUR": {"value": 85.20}
            }
        }
        mock_get.return_value = mock_response

        result = get_currency_rates(self.test_currencies)

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["USD"], 75.50)
        self.assertEqual(result["data"]["EUR"], 85.20)
        mock_get.assert_called_once()

    @patch.dict(os.environ, {"CURRENCY_API_KEY": "test_key"})
    @patch('src.services.requests.get')
    def test_get_currency_rates_api_error(self, mock_get):
        """Тест обработки ошибки API валют."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": {"message": "Invalid API key"}
        }
        mock_get.return_value = mock_response

        result = get_currency_rates(self.test_currencies)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid API key")

    def test_get_currency_rates_no_api_key(self):
        """Тест поведения при отсутствии API ключа."""
        with patch.dict(os.environ, {"CURRENCY_API_KEY": ""}):
            result = get_currency_rates(self.test_currencies)
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "Currency API key not configured")

    def test_get_currency_rates_no_currencies(self):
        """Тест поведения при пустом списке валют."""
        with patch.dict(os.environ, {"CURRENCY_API_KEY": "test_key"}):
            result = get_currency_rates([])
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "No currencies specified")

    @patch.dict(os.environ, {"STOCKS_API_KEY": "test_key"})
    @patch('src.services.requests.get')
    def test_get_stock_prices_success(self, mock_get):
        """Тест успешного получения цен акций."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"Global Quote": {"05. price": "150.50"}},
            {"Global Quote": {"05. price": "2750.20"}}
        ]
        mock_get.return_value = mock_response

        result = get_stock_prices(self.test_stocks)

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["AAPL"], 150.50)
        self.assertEqual(result["data"]["GOOGL"], 2750.20)
        self.assertEqual(mock_get.call_count, 2)

    @patch.dict(os.environ, {"STOCKS_API_KEY": "test_key"})
    def test_get_stock_prices_no_api_key(self):
        """Тест поведения при отсутствии API ключа для акций."""
        with patch.dict(os.environ, {"STOCKS_API_KEY": ""}):
            result = get_stock_prices(self.test_stocks)
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "Stocks API key not configured")

    def test_get_stock_prices_no_stocks(self):
        """Тест поведения при пустом списке акций."""
        with patch.dict(os.environ, {"STOCKS_API_KEY": "test_key"}):
            result = get_stock_prices([])
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "No stocks specified")

    @patch('src.services.get_currency_rates')
    @patch('src.services.get_stock_prices')
    def test_get_financial_data_success(self, mock_stocks, mock_currency):
        """Тест успешного получения всех финансовых данных."""
        mock_currency.return_value = {
            "success": True,
            "data": {"USD": 75.50, "EUR": 85.20}
        }
        mock_stocks.return_value = {
            "success": True,
            "data": {"AAPL": 150.50, "GOOGL": 2750.20}
        }

        result = get_financial_data(self.test_settings)

        self.assertEqual(result["currencies"]["USD"], 75.50)
        self.assertEqual(result["stocks"]["AAPL"], 150.50)
        mock_currency.assert_called_once_with(self.test_currencies)
        mock_stocks.assert_called_once_with(self.test_stocks)

    @patch('src.services.get_currency_rates')
    @patch('src.services.get_stock_prices')
    def test_get_financial_data_partial_failure(self, mock_stocks, mock_currency):
        """Тест частичного отказа сервисов."""
        mock_currency.return_value = {
            "success": False,
            "error": "Currency API error"
        }
        mock_stocks.return_value = {
            "success": True,
            "data": {"AAPL": 150.50}
        }

        result = get_financial_data(self.test_settings)

        self.assertEqual(result["currencies"], {})
        self.assertEqual(result["stocks"]["AAPL"], 150.50)

    def test_get_financial_data_empty_settings(self):
        """Тест с пустыми настройками."""
        result = get_financial_data({})
        self.assertEqual(result["currencies"], {})
        self.assertEqual(result["stocks"], {})


if __name__ == '__main__':
    unittest.main()
