import logging
from typing import Any, Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


def main_page(date: str,
              df: pd.DataFrame,
              settings: Dict[str, Any],
              financial_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Формирует данные для отображения на главной странице.
    """
    try:
        logger.info("Формирование главной страницы для времени %s", date)

        current_balance = calculate_current_balance(df, date)
        recent_transactions = get_recent_transactions(df, date, limit=5)

        response = {
            "current_balance": current_balance,
            "recent_transactions": recent_transactions,
            "financial_data": financial_data or {},
            "settings": settings
        }

        logger.info("Главная страница сформирована успешно.")
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
    Возвращает структуру с общей статистикой и краткими отчетами.
    """
    try:
        logger.info("Формирование страницы событий для даты %s, период: %s", date, period)

        filtered_df = filter_transactions_by_date(df, date, period)

        # Если операций нет
        if filtered_df.empty:
            logger.warning("Нет операций для даты %s и периода %s", date, period)
            return {
                "status": "empty",
                "message": "No transactions found for selected period",
                "reports": []
            }

        stats = get_transaction_stats(filtered_df) or {}
        stats.setdefault("total_income", 0.0)
        stats.setdefault("total_expenses", 0.0)
        stats.setdefault("transaction_count", len(filtered_df))
        stats.setdefault("average_transaction", 0.0)
        stats.setdefault("categories", {})

        total_income = stats["total_income"]
        total_expenses = stats["total_expenses"]
        net_balance = total_income + total_expenses

        income_vs_expenses = {
            "type": "income_vs_expenses",
            "summary": (
                f"Доходы превышают расходы на {abs(net_balance):,.2f} ₽"
                if net_balance >= 0
                else f"Расходы превышают доходы на {abs(net_balance):,.2f} ₽"
            )
        }

        top_category = None
        if stats["categories"]:
            most_used = max(stats["categories"], key=stats["categories"].get)
            top_category = {
                "type": "top_category",
                "summary": f"Самая частая категория: {most_used} ({stats['categories'][most_used]} операций)"
            }

        response = {
            "date": date,
            "period": period,
            "transaction_count": len(filtered_df),
            "transaction_stats": stats,
            "reports": [income_vs_expenses]
        }

        if top_category:
            response["reports"].append(top_category)

        logger.info("Страница событий успешно сформирована.")
        return response

    except Exception as e:
        logger.error("Ошибка при формировании страницы событий: %s", e)
        return {"error": f"Failed to generate events page: {str(e)}"}


def calculate_current_balance(df: pd.DataFrame, timestamp: str) -> float:
    """Вычисляет текущий баланс на указанный момент времени."""
    try:
        if df.empty:
            return 0.0

        df['Дата операции'] = pd.to_datetime(df['Дата операции'])
        mask = df['Дата операции'] <= pd.to_datetime(timestamp)
        filtered_df = df.loc[mask].copy()

        if filtered_df.empty:
            return 0.0

        income = filtered_df[filtered_df['Сумма операции'] > 0]['Сумма операции'].sum()
        expenses = filtered_df[filtered_df['Сумма операции'] < 0]['Сумма операции'].sum()

        return float(income + expenses)
    except Exception as e:
        logger.error("Ошибка расчета баланса: %s", e)
        return 0.0


def get_recent_transactions(df: pd.DataFrame,
                            timestamp: str,
                            limit: int = 5) -> List[Dict[str, Any]]:
    """Получает последние операции до указанного времени."""
    try:
        if df.empty:
            return []

        df['Дата операции'] = pd.to_datetime(df['Дата операции'])
        mask = df['Дата операции'] <= pd.to_datetime(timestamp)
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
    """Фильтрует операции по указанной дате и периоду (D/W/M)."""
    try:
        if df.empty:
            return pd.DataFrame()

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
    """Собирает статистику по операциям."""
    try:
        if df.empty:
            return {
                "total_income": 0.0,
                "total_expenses": 0.0,
                "transaction_count": 0,
                "average_transaction": 0.0,
                "categories": {}
            }

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
