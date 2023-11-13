from datetime import datetime
from decimal import Decimal
from common.utils import JsonSerializable

class Stock(JsonSerializable):
    def __init__(self, symbol: str, open_price: Decimal, high: Decimal, low: Decimal,
                 price: Decimal, volume: int, latest_trading_day: datetime,
                 previous_close: Decimal, change: Decimal, change_percent: Decimal,
                 created: datetime = None, modified: datetime = None):
        self.symbol = symbol
        self.open_price = open_price
        self.high = high
        self.low = low
        self.price = price
        self.volume = volume
        self.latest_trading_day = latest_trading_day
        self.previous_close = previous_close
        self.change = change
        self.change_percent = change_percent
        self.created = created
        self.modified = modified