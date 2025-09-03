import pandas as pd
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "operations.xlsx"


def load_operations(file_path: Path | None = None) -> pd.DataFrame:
    """
    Загружает Excel-файл с операциями.

    """
    try:
        path = file_path or DATA_PATH
        logging.info(f"Загрузка операций из файла: {path}")
        df = pd.read_excel(path, parse_dates=["Дата операции"])
        return df
    except Exception as e:
        logging.error(f"Ошибка при загрузке Excel: {e}", exc_info=True)
        raise
