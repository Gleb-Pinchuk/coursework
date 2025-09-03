import pandas as pd
from unittest.mock import patch
from src import main


def test_main_run_with_mock(capsys):
    df_mock = pd.DataFrame(
        [{"Дата операции": pd.Timestamp("2020-05-20"), "Сумма операции": 200}]
    )
    settings_mock = {"currencies": ["RUB"]}

    with patch("src.utils.load_operations", return_value=df_mock), \
         patch("src.main.load_user_settings", return_value=settings_mock):
        main.run()

    # проверим, что в stdout что-то вывелось
    captured = capsys.readouterr()
    assert "Главная" in captured.out or "main" in captured.out
