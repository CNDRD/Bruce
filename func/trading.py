import requests


def get_current_price(stock: str) -> float | None:
    stock = stock.upper()
    request_url = "https://api.redstone.finance/prices"
    queries = {"provider": "redstone", "symbol": stock}
    response = requests.request("GET", request_url, params=queries)

    if not response.json():
        return None

    if response.json() is None:
        return None
    return response.json()[0].get("value")


def get_multiple_prices(stocks) -> dict[str, float]:
    x = {}
    for stock in stocks:
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
