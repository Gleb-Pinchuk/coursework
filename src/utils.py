import pandas as pd


def read_transactions_excel(file_path: str) -> pd.DataFrame:
    """
    Читает Excel-файл с транзакциями.
    """
    df = pd.read_excel(file_path, parse_dates=["Дата операции"])

    df = df.rename(columns={
        "Дата операции": "date",
        "Номер карты": "card",
        "Сумма операции": "amount",
        "Категория": "category",
        "Описание": "description",
        "Валюта операции": "currency",
    })

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["card"] = df["card"].astype(str).str.strip()

    df = df.dropna(subset=["amount"])

    return df
