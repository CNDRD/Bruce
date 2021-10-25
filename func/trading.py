def get_trading_buy_db(stock: str, amount: int, bought_at: float):
    data = {
        stock: {
            "amount": amount,
            "boughtAt": bought_at
        }
    }
    return data
