class Stock:
    def __init__(self, **kwargs):
        self.symbol = kwargs.get('symbol', 'Unknown')
        self.open_price = float(kwargs.get('open', 0))
        self.high = float(kwargs.get('high', 0))
        self.low = float(kwargs.get('low', 0))
        self.price = float(kwargs.get('price', 0))
        self.volume = int(kwargs.get('volume', 0))
        self.previous_close = float(kwargs.get('previous_close', 0))
        self.change = float(kwargs.get('change', 0))
        self.change_percent = float(kwargs.get('change_percent', '0%').strip('%')) / 100
        self.shares = kwargs.get('shares', 1)

    def volatility(self):
        return self.high - self.low

    def performance_score(self):
        return self.change_percent * self.volume

class Broker:
    def __init__(self, name, rarity, stocks):
        self.name = name
        self.rarity = rarity
        self.stocks = stocks
        self.power = 0
        self.defense = 0
        self.life = 0
        self.life_max = 0
        self.stonks = 0
        self.recalculate_stats()

    def add_stock(self, stock):
        self.stocks.append(stock)
        self.recalculate_stats()

    def recalculate_stats(self):
        self.power = round(self.calculate_power())
        self.defense = round(self.calculate_defense())
        self.life = round(self.calculate_life())
        self.life_max = self.life
        self.stonks = round(self.calculate_stonks())

    def calculate_power(self):
        if not self.stocks:
            return 0
        base_power = sum((stock.price * self.diminishing_returns(stock.shares)) / 100 for stock in self.stocks)
        rarity_modifier = 1.03 ** self.rarity
        performance_modifier = 1 + sum(stock.performance_score() for stock in self.stocks) / (5000 * len(self.stocks)) if self.stocks else 1
        return base_power * rarity_modifier * performance_modifier

    def calculate_defense(self):
        base_defense = sum(((1 / stock.volatility()) * self.diminishing_returns(stock.shares)) / 10 for stock in self.stocks)
        rarity_modifier = 1.02 ** self.rarity
        performance_modifier = 1 + sum(stock.performance_score() for stock in self.stocks) / (500 * len(self.stocks)) if self.stocks else 1
        return base_defense * rarity_modifier * performance_modifier

    def diminishing_returns(self, shares):
        return sum(1 / (i + 1)**0.5 for i in range(shares))

    def calculate_life(self):
        base_life = sum((stock.price * self.diminishing_returns(stock.shares)) / 10 for stock in self.stocks)  # Adjusted calculation
        rarity_modifier = 1.03 ** self.rarity  # Rarity modifier
        calculated_life = base_life * rarity_modifier
        return round(calculated_life) if calculated_life > 0 else 1  # Ensure life is at least 1

    def calculate_stonks(self):
        return (self.power + self.defense + self.life) / 3

def battle(broker1, broker2, rounds=500):
    broker1.life = broker1.life_max
    broker2.life = broker2.life_max
    for round in range(1, rounds + 1):
        print(f"Round {round}")
        print(f"{broker1.name} - Life: {broker1.life}/{broker1.life_max}, Power: {broker1.power}, Defense: {broker1.defense}")
        print(f"{broker2.name} - Life: {broker2.life}/{broker2.life_max}, Power: {broker2.power}, Defense: {broker2.defense}")

        damage_to_broker2 = max(1, broker1.power - broker2.defense)
        broker2.life = max(0, broker2.life - damage_to_broker2)
        print(f"{broker1.name} deals {damage_to_broker2} damage to {broker2.name}")

        if broker2.life <= 0:
            print(f"{broker1.name} wins!")
            return

        damage_to_broker1 = max(1, broker2.power - broker1.defense)
        broker1.life = max(0, broker1.life - damage_to_broker1)
        print(f"{broker2.name} deals {damage_to_broker1} damage to {broker1.name}")

        if broker1.life <= 0:
            print(f"{broker2.name} wins!")
            return

    if broker1.life > 0 and broker2.life > 0:
        print("The battle ended in a draw.")

# Test Data with adjustable shares
stocks_broker1 = [
    Stock(symbol='COIN', open='94.4000', high='96.2185', low='91.8000', price='92.9200', volume='9853318', previous_close='92.8600', shares=1000, change='0.0600', change_percent='0.0646%'),
]

stocks_broker2 = [
    Stock(symbol='AAPL', open='150.4000', high='153.2185', low='148.8000', price='149.9200', volume='10853318', previous_close='150.4000', shares=10, change='-0.4800', change_percent='-0.3190%'),
    Stock(symbol='NFLX', open='500.0000', high='510.0000', low='495.0000', price='505.0000', volume='5000000', previous_close='500.0000', shares=10, change='5.0000', change_percent='1.0000%'),
    Stock(symbol='FB', open='270.0000', high='275.0000', low='265.0000', price='272.0000', volume='6000000', previous_close='270.0000', shares=10, change='2.0000', change_percent='0.7407%'),
    Stock(symbol='BABA', open='200.0000', high='205.0000', low='195.0000', price='202.0000', volume='4000000', previous_close='200.0000', shares=10, change='2.0000', change_percent='1.0000%'),
    Stock(symbol='V', open='220.0000', high='225.0000', low='215.0000', price='222.0000', volume='3500000', previous_close='220.0000', shares=10, change='2.0000', change_percent='0.9091%'),
    Stock(symbol='JPM', open='130.0000', high='133.0000', low='128.0000', price='131.0000', volume='4500000', previous_close='130.0000', shares=10, change='1.0000', change_percent='0.7692%'),
    Stock(symbol='INTC', open='50.0000', high='51.5000', low='49.5000', price='50.5000', volume='8000000', previous_close='50.0000', shares=100, change='0.5000', change_percent='1.0000%')
]

# Create Brokers
broker1 = Broker(name="Alice", rarity=1, stocks=stocks_broker1)
broker2 = Broker(name="Bob", rarity=5, stocks=stocks_broker2)

# Battle Simulation with rounds
battle_result = battle(broker1, broker2)
