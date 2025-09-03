import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


def main_page(date: str, df: pd.DataFrame, settings: dict) -> dict:
    date = pd.to_datetime(date)
    summary = {"total": float(df["Сумма операции"].sum())}
    return {
        "page": "main",
        "date": date.isoformat(),
        "transactions_count": len(df),
        "summary": summary,
        "user_settings": settings,
    }


def events_page(date: str, df: pd.DataFrame, settings: dict, period: str = "M") -> dict:
    summary = df.groupby(pd.Grouper(key="Дата операции", freq=period))[
        "Сумма операции"
    ].sum()
    return {
        "page": "events",
        "date": pd.to_datetime(date).isoformat(),
        "settings": settings,
        "events": True,
        "summary": summary.to_dict(),
    }
