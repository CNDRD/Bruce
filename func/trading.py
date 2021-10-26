import requests
import os
from dotenv import load_dotenv
load_dotenv()


api_url = "https://api.twelvedata.com/price"
api_key = os.getenv("TWELVE_DATA_API_KEY")


def get_current_price(stock: str) -> float:
    stock = stock.replace('-', '/')
    request_url = f"https://api.twelvedata.com/price"
    querystring = {"symbol": stock, "format": "json", "apikey": api_key}
    response = requests.request("GET", request_url, params=querystring)
    return round(float(response.json().get('price')), 2)


def get_multiple_prices(stocks) -> dict[str, float]:
    x = {}
    for stock in stocks:
        stock = stock.replace('-', '/')
        x[stock] = get_current_price(stock)
    return x


def get_trading_buy_db(stock: str, amount: int, bought_at: float) -> dict[dict[str, int]]:
    stock = stock.replace('/', '-')
    data = {
        stock: {
            "amount": amount,
            "boughtAt": bought_at
        }
    }
    return data
