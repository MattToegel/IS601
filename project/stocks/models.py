from datetime import datetime
from decimal import Decimal
from common.utils import JsonSerializable

class Stock(JsonSerializable):
    def __init__(self, id: int, symbol: str, open: Decimal, high: Decimal, low: Decimal,
                 price: Decimal, volume: int, latest_trading_day: datetime,
                 previous_close: Decimal, change: Decimal, change_percent: Decimal,
                 created: datetime = None, modified: datetime = None, shares: int = 1):
        self.id = id
        self.symbol = symbol
        self.open = open
        self.high = high
        self.low = low
        self.price = price
        self.volume = volume
        self.latest_trading_day = latest_trading_day
        self.previous_close = previous_close
        self.change = change
        self.change_percent = Decimal(change_percent)
        self.created = created
        self.modified = modified
        self.shares = shares if shares is not None else 1
    def volatility(self):
        return self.high - self.low

    def performance_score(self):
        return self.change_percent # * (self.shares*self.price) # * self.volume
