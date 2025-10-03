import unittest
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from unittest.mock import patch

from src.views import (main_page, events_page, calculate_current_balance,
                       get_recent_transactions, filter_transactions_by_date,
                       get_transaction_stats)


class TestViews(unittest.TestCase):
    """Тесты для модуля представлений."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.test_data = pd.DataFrame({
            'Дата операции': [
                '2020-05-01 10:00:00', '2020-05-15 14:30:00',
                '2020-05-20 09:15:00', '2020-05-20 16:45:00'
            ],
            'Сумма операции': [1000.0, -500.0, 2000.0, -300.0],
            'Категория': ['Income', 'Food', 'Income', 'Transport'],
            'Описание': ['Salary', 'Lunch', 'Bonus', 'Taxi']
        })
        self.test_data['Дата операции'] = pd.to_datetime(self.test_data['Дата операции'])

        self.test_settings = {"currencies": ["USD"], "stocks": ["AAPL"]}
        self.test_financial_data = {
            "currencies": {"USD": 75.50},
            "stocks": {"AAPL": 150.50}
        }


    def test_calculate_current_balance(self):
        """Тест расчета текущего баланса."""
        balance = calculate_current_balance(self.test_data, "2020-05-20 12:00:00")
        expected = 1000.0 - 500.0 + 2000.0  # 2500.0
        self.assertEqual(balance, expected)


    def test_calculate_current_balance_empty(self):
        """Тест расчета баланса для пустых данных."""
        empty_df = pd.DataFrame()
        balance = calculate_current_balance(empty_df, "2020-05-20 12:00:00")
        self.assertEqual(balance, 0.0)


    def test_get_recent_transactions(self):
        """Тест получения последних операций."""
        transactions = get_recent_transactions(self.test_data, "2020-05-20 12:00:00", 2)
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]["amount"], 2000.0)  # Самая recent


    def test_filter_transactions_by_date_day(self):
        """Тест фильтрации операций по дню."""
        filtered = filter_transactions_by_date(self.test_data, "2020-05-20", "D")
        self.assertEqual(len(filtered), 2)


    def test_filter_transactions_by_date_month(self):
        """Тест фильтрации операций по месяцу."""
        filtered = filter_transactions_by_date(self.test_data, "2020-05-15", "M")
        self.assertEqual(len(filtered), 4)


    def test_get_transaction_stats(self):
        """Тест сбора статистики по операциям."""
        stats = get_transaction_stats(self.test_data)
        self.assertEqual(stats["total_income"], 3000.0)
        self.assertEqual(stats["total_expenses"], -800.0)
        self.assertEqual(stats["transaction_count"], 4)


    @patch('src.views.calculate_current_balance')
    @patch('src.views.get_recent_transactions')
    def test_main_page_success(self, mock_recent, mock_balance):
        """Тест успешного формирования главной страницы."""
        mock_balance.return_value = 2500.0
        mock_recent.return_value = [{"amount": 1000.0}]

        result = main_page(
            "2020-05-20 15:45:00",
            self.test_data,
            self.test_settings,
            self.test_financial_data
        )

        self.assertEqual(result["current_balance"], 2500.0)
        self.assertEqual(len(result["recent_transactions"]), 1)
        self.assertEqual(result["financial_data"], self.test_financial_data)
        mock_balance.assert_called_once()
        mock_recent.assert_called_once()


    def test_main_page_error(self):
        """Тест обработки ошибок в главной странице."""
        with patch('src.views.calculate_current_balance', side_effect=Exception("Test error")):
            result = main_page(
                "2020-05-20 15:45:00",
                self.test_data,
                self.test_settings,
                self.test_financial_data
            )
            self.assertIn("error", result)


    @patch('src.views.filter_transactions_by_date')
    @patch('src.views.get_transaction_stats')
    def test_events_page_success(self, mock_stats, mock_filter):
        """Тест успешного формирования страницы событий."""
        mock_filter.return_value = self.test_data
        mock_stats.return_value = {"total_income": 3000.0}

        result = events_page(
            "2020-05-20",
            self.test_data,
            self.test_settings,
            "D"
        )

        self.assertEqual(result["date"], "2020-05-20")
        self.assertEqual(result["period"], "D")
        self.assertEqual(result["transaction_stats"]["total_income"], 3000.0)
        mock_filter.assert_called_once()
        mock_stats.assert_called_once()


    def test_events_page_no_transactions(self):
        """Тест страницы событий без операций."""
        empty_df = pd.DataFrame()
        result = events_page(
            "2020-05-20",
            empty_df,
            self.test_settings,
            "D"
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "No transactions found for selected period")


if __name__ == '__main__':
    unittest.main()
