import unittest
from unittest.mock import patch, mock_open
import pandas as pd
import numpy as np

from src.utils import load_operations, format_currency


class TestUtils(unittest.TestCase):
    """Тесты для вспомогательных утилит."""


    @patch('pandas.read_excel')
    def test_load_operations_success(self, mock_read_excel):
        """Тест успешной загрузки операций."""
        test_data = pd.DataFrame({
            'Дата операции': ['2020-05-01', '2020-05-02'],
            'Сумма операции': [100.0, -50.0],
            'Категория': ['Income', 'Food']
        })
        mock_read_excel.return_value = test_data

        result = load_operations('test_path.xlsx')

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        mock_read_excel.assert_called_once_with('test_path.xlsx')


    @patch('pandas.read_excel')
    def test_load_operations_missing_columns(self, mock_read_excel):
        """Тест загрузки с отсутствующими колонками."""
        test_data = pd.DataFrame({'Wrong_Column': [1, 2]})
        mock_read_excel.return_value = test_data

        result = load_operations('test_path.xlsx')
        self.assertIsNone(result)


    @patch('pandas.read_excel', side_effect=FileNotFoundError)
    def test_load_operations_file_not_found(self, mock_read_excel):
        """Тест загрузки несуществующего файла."""
        result = load_operations('nonexistent.xlsx')
        self.assertIsNone(result)


    def test_format_currency_rub(self):
        """Тест форматирования рублёвой суммы."""
        result = format_currency(1234.56, "RUB")
        self.assertEqual(result, "1,234.56 ₽")


    def test_format_currency_usd(self):
        """Тест форматирования долларовой суммы."""
        result = format_currency(1234.56, "USD")
        self.assertEqual(result, "$1,234.56")


    def test_format_currency_eur(self):
        """Тест форматирования евро суммы."""
        result = format_currency(1234.56, "EUR")
        self.assertEqual(result, "€1,234.56")


    def test_format_currency_default(self):
        """Тест форматирования с валютой по умолчанию."""
        result = format_currency(1234.56)
        self.assertEqual(result, "1,234.56 ₽")


    def test_format_currency_invalid_amount(self):
        """Тест форматирования нечислового значения."""
        result = format_currency("invalid", "USD")
        self.assertEqual(result, "invalid")


if __name__ == '__main__':
    unittest.main()
