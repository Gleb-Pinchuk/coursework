import pandas as pd
from src import reports


def test_spending_by_category(tmp_path):
    df = pd.DataFrame(
        [
            {"Дата операции": pd.Timestamp("2020-05-01"), "Категория": "Еда", "Сумма операции": 100},
            {"Дата операции": pd.Timestamp("2020-06-01"), "Категория": "Еда", "Сумма операции": 200},
        ]
    )

    result = reports.spending_by_category(df, "Еда", "2020-07-01")
    assert "total" in result
    assert result["total"] == 300


def test_spending_by_weekday():
    df = pd.DataFrame(
        [{"Дата операции": pd.Timestamp("2020-05-20"), "Сумма операции": 150}]
    )

    result = reports.spending_by_weekday(df, "2020-07-01")
    assert "data" in result


def test_spending_by_workday():
    df = pd.DataFrame(
        [{"Дата операции": pd.Timestamp("2020-05-20"), "Сумма операции": 150}]
    )

    result = reports.spending_by_workday(df, "2020-07-01")
    assert "data" in result
    assert "workdays" in result["data"]
