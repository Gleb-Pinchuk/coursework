import logging
from typing import Any, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def main_page(timestamp: str,
              df: pd.DataFrame,
              settings: Dict[str, Any],
              financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Формирует данные для отображения на главной странице.
    """
    try:
        logger.info("Формирование главной страницы для времени %s", timestamp)

        current_balance = calculate_current_balance(df, timestamp)

        recent_transactions = get_recent_transactions(df, timestamp, limit=5)

        response = {
            "current_balance": current_balance,
            "recent_transactions": recent_transactions,
            "financial_data": financial_data  # Добавлены данные о валютах и акциях
        }

        logger.info("Главная страница сформирована. Баланс: %s, Валют: %d, Акций: %d",
                    current_balance,
                    len(financial_data.get("currencies", {})),
                    len(financial_data.get("stocks", {})))

        return response

    except Exception as e:
        logger.error("Ошибка при формировании главной страницы: %s", e)
        return {"error": f"Failed to generate main page: {str(e)}"}


def events_page(date: str,
                df: pd.DataFrame,
                settings: Dict[str, Any],
                period: str = "M") -> Dict[str, Any]:
    """
    Формирует данные для страницы событий и отчетов.
    """
    try:
        logger.info("Формирование страницы событий для даты %s, период: %s", date, period)

        # Фильтрация операций по дате
        filtered_df = filter_transactions_by_date(df, date, period)

        if filtered_df.empty:
            logger.warning("Нет операций для даты %s и периода %s", date, period)
            return {"message": "No transactions found for selected period"}

        transaction_stats = get_transaction_stats(filtered_df)

        response = {
            "date": date,
            "period": period,
            "transaction_count": len(filtered_df),
            "transaction_stats": transaction_stats,
            # Место для добавления сгенерированных отчетов
            "reports": []
        }

        logger.info("Страница событий сформирована. Найдено операций: %d", len(filtered_df))

        return response

    except Exception as e:
        logger.error("Ошибка при формировании страницы событий: %s", e)
        return {"error": f"Failed to generate events page: {str(e)}"}


def calculate_current_balance(df: pd.DataFrame, timestamp: str) -> float:
    """
    Вычисляет текущий баланс на указанный момент времени.
    """
    try:
        mask = pd.to_datetime(df['Дата операции']) <= pd.to_datetime(timestamp)
        filtered_df = df.loc[mask].copy()

        # Расчет баланса
        income = filtered_df[filtered_df['Сумма операции'] > 0]['Сумма операции'].sum()
        expenses = filtered_df[filtered_df['Сумма операции'] < 0]['Сумма операции'].sum()

        return income + expenses  # expenses уже отрицательные

    except Exception as e:
        logger.error("Ошибка расчета баланса: %s", e)
        return 0.0


def get_recent_transactions(df: pd.DataFrame,
                            timestamp: str,
                            limit: int = 5) -> list[Dict[str, Any]]:
    """
    Получает последние операции до указанного времени.
    """
    try:
        mask = pd.to_datetime(df['Дата операции']) <= pd.to_datetime(timestamp)
        filtered_df = df.loc[mask].copy()

        filtered_df = filtered_df.sort_values('Дата операции', ascending=False)
        recent_df = filtered_df.head(limit)

        transactions = []
        for _, row in recent_df.iterrows():
            transactions.append({
                "date": str(row['Дата операции']),
                "amount": float(row['Сумма операции']),
                "category": row.get('Категория', 'Не указана'),
                "description": row.get('Описание', '')
            })

        return transactions

    except Exception as e:
        logger.error("Ошибка получения последних операций: %s", e)
        return []


def filter_transactions_by_date(df: pd.DataFrame,
                                date: str,
                                period: str) -> pd.DataFrame:
    """
    Фильтрует операции по указанной дате и периоду.
    """
    try:
        base_date = pd.to_datetime(date)
        df['Дата операции'] = pd.to_datetime(df['Дата операции'])

        if period == "D":
            mask = df['Дата операции'].dt.date == base_date.date()
        elif period == "W":
            week_start = base_date - pd.Timedelta(days=base_date.weekday())
            week_end = week_start + pd.Timedelta(days=6)
            mask = (df['Дата операции'] >= week_start) & (df['Дата операции'] <= week_end)
        elif period == "M":
            mask = (df['Дата операции'].dt.year == base_date.year) & \
                   (df['Дата операции'].dt.month == base_date.month)
        else:
            logger.warning("Неизвестный период: %s", period)
            return pd.DataFrame()

        return df.loc[mask].copy()

    except Exception as e:
        logger.error("Ошибка фильтрации операций: %s", e)
        return pd.DataFrame()


def get_transaction_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Собирает статистику по операциям.
    """
    try:
        stats = {
            "total_income": float(df[df['Сумма операции'] > 0]['Сумма операции'].sum()),
            "total_expenses": float(df[df['Сумма операции'] < 0]['Сумма операции'].sum()),
            "transaction_count": len(df),
            "average_transaction": float(df['Сумма операции'].mean()),
            "categories": df['Категория'].value_counts().to_dict()
        }

        return stats

    except Exception as e:
        logger.error("Ошибка расчета статистики: %s", e)
        return {}
