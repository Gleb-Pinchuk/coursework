from pathlib import Path
from typing import Optional

import logging
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "operations.xlsx"

logger = logging.getLogger(__name__)


def load_operations(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Загружает Excel-файл с операциями.
    """
    try:
        path = file_path or DATA_PATH
        logger.info("Загрузка операций из файла: %s", path)
        df: pd.DataFrame = pd.read_excel(path, parse_dates=["Дата операции"])
        return df
    except Exception as e:
        logger.error("Ошибка при загрузке Excel: %s", e, exc_info=True)
        raise
