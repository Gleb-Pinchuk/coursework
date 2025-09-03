import pandas as pd
from unittest.mock import patch
from src import utils


def test_load_operations_with_mock(tmp_path):
    df_mock = pd.DataFrame(
        [
            {"Дата операции": pd.Timestamp("2020-05-01"), "Сумма операции": 100},
            {"Дата операции": pd.Timestamp("2020-06-01"), "Сумма операции": 200},
        ]
    )

    with patch("src.utils.pd.read_excel", return_value=df_mock) as mock_read:
        df = utils.load_operations()

    mock_read.assert_called_once_with(utils.DATA_PATH, parse_dates=["Дата операции"])

    pd.testing.assert_frame_equal(df, df_mock)
