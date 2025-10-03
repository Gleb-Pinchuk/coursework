import pandas as pd
from src import reports


def test_spending_by_category():
    df = pd.DataFrame(
        [
            {"Дата операции": pd.Timestamp("2020-05-01"), "Категория": "Еда", "Сумма операции": 100},
            {"Дата операции": pd.Timestamp("2020-06-01"), "Категория": "Еда", "Сумма операции": 200},
            {"Дата операции": pd.Timestamp("2020-06-15"), "Категория": "Транспорт", "Сумма операции": 50},
        ]
    )

    result = reports.spending_by_category(df, "Еда", "2020-07-01")
    assert result["report"] == "spending_by_category"
    assert "total" in result["data"]
    assert result["data"]["total"] == 300  # 100 + 200


def test_spending_by_weekday():
    df = pd.DataFrame(
        [
            {"Дата операции": pd.Timestamp("2020-05-18"), "Сумма операции": 100},  # Monday
            {"Дата операции": pd.Timestamp("2020-05-19"), "Сумма операции": 50},   # Tuesday
            {"Дата операции": pd.Timestamp("2020-05-23"), "Сумма операции": 30},   # Saturday
        ]
    )

    result = reports.spending_by_weekday(df, "2020-07-01")
    assert result["report"] == "spending_by_weekday"
    assert "data" in result
    # Проверяем суммы по дням недели
    assert result["data"]["Monday"] == 100
    assert result["data"]["Tuesday"] == 50
    assert result["data"]["Saturday"] == 30


def test_spending_by_workday():
    df = pd.DataFrame(
        [
            {"Дата операции": pd.Timestamp("2020-05-18"), "Сумма операции": 100},  # Monday
            {"Дата операции": pd.Timestamp("2020-05-19"), "Сумма операции": 50},   # Tuesday
            {"Дата операции": pd.Timestamp("2020-05-23"), "Сумма операции": 30},   # Saturday
        ]
    )

    result = reports.spending_by_workday(df, "2020-07-01")
    assert result["report"] == "spending_by_workday"
    assert "data" in result
    # По новой логике функции возвращается среднее
    assert result["data"]["workday"] == (100 + 50) / 2
    assert result["data"]["weekend"] == 30
