import pandas as pd
from unittest.mock import patch
from src import views


def test_main_page_with_mock():
    df_mock = pd.DataFrame(
        [{"Дата операции": pd.Timestamp("2020-05-20"), "Сумма операции": 200}]
    )
    settings_mock = {"currencies": ["RUB"]}

    with patch("src.utils.load_operations", return_value=df_mock):
        result = views.main_page("2020-05-20 15:45:00", df_mock, settings_mock)

    assert "summary" in result
    assert result["summary"]["total"] == 200


def test_events_page_with_mock():
    df_mock = pd.DataFrame(
        [{"Дата операции": pd.Timestamp("2020-05-20"), "Сумма операции": 200}]
    )
    settings_mock = {}

    with patch("src.utils.load_operations", return_value=df_mock):
        result = views.events_page("2020-05-20", df_mock, settings_mock, period="M")

    assert "events" in result
    assert "summary" in result
    assert any(val == 200 for val in result["summary"].values())
