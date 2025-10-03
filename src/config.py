import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCKS_API_KEY = os.getenv("STOCKS_API_KEY")

CURRENCY_BASE_URL = os.getenv(
    "CURRENCY_BASE_URL", "https://api.currencyprovider.com/latest"
)
STOCKS_BASE_URL = os.getenv(
    "STOCKS_BASE_URL", "https://api.stocksprovider.com/query"
)
