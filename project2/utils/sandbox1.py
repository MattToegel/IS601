import random
import math

class Stock:
    def __init__(self, symbol, open_price, high_price, low_price, current_price, volume, shares, avg_volume_7d, change_percent):
        self.symbol = symbol
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.current_price = current_price
        self.volume = volume
        self.shares = shares
        self.avg_volume_7d = avg_volume_7d
        self.change_percent = float(change_percent.strip('%')) / 100

    def shares_factor(self):
        return self.shares

    def diminishing_return_factor(self):
        return math.sqrt(self.shares)

    def lower_power_factor(self):
        return (self.current_price / self.low_price) * self.diminishing_return_factor() if self.low_price else 0

    def higher_power_factor(self):
        return (self.current_price / self.high_price) * self.diminishing_return_factor() if self.high_price else 0

    def volume_factor(self):
        return (self.volume / self.avg_volume_7d) * self.diminishing_return_factor() if self.avg_volume_7d else 0

    def diminishing_value(self):
        return self.current_price * self.diminishing_return_factor()

    def value(self):
        return self.current_price * self.shares

class Broker:
    POWER_MOD = 1.15
    VOLUME_MOD = 1.23
    LIFE_MOD = 1.65
    RARITY_IMPACT_MOD = 3
    PORTFOLIO_POWER_MODIFIER = 0.001

    def __init__(self, name, rarity, initial_stocks):
        self.name = name
        self.rarity = rarity
        self.stocks = initial_stocks[:rarity]
        self.stonks = 0

    def add_stock(self, stock):
        if len(self.stocks) < self.rarity:
            self.stocks.append(stock)
        else:
            print(f"{self.name} cannot add more stocks. Maximum diversity reached.")

    def calculate_life(self, shares_factor, rarity_impact):
        base_life = 100
        self.life = ((base_life + math.sqrt(shares_factor) * 10) * Broker.LIFE_MOD) * rarity_impact
        self.life_max = self.life

    def calculate_power(self, rarity_impact):
        all_lower_powers = [stock.lower_power_factor() for stock in self.stocks]
        all_higher_powers = [stock.higher_power_factor() for stock in self.stocks]

        total_lower_power = sum(all_lower_powers) * rarity_impact
        total_higher_power = sum(all_higher_powers) * rarity_impact

        self.power = (total_lower_power, total_higher_power)
        self.average_power = (total_lower_power + total_higher_power) / 2

    def calculate_defense(self, rarity_impact):
        volume_factor_sum = sum(stock.volume_factor()**Broker.VOLUME_MOD for stock in self.stocks)
        self.defense = volume_factor_sum * rarity_impact

    def calculate_portfolio_performance(self):
        if self.stocks:
            total_change_percent = sum(stock.change_percent for stock in self.stocks)
            self.portfolio_performance = total_change_percent / len(self.stocks)
        else:
            self.portfolio_performance = 0

    def calculate_stonks(self):
        # Adjust the scaling factors for a balanced contribution from each component
        #scaled_power = self.average_power / 100  # Adjusted scaling for power
        #scaled_defense = self.defense / 100      # Adjusted scaling for defense
        #scaled_life = self.life_max / 500        # Adjusted scaling for life
        scaled_power = math.sqrt(self.average_power)
        scaled_defense = math.sqrt(self.defense)
        scaled_life = math.sqrt(self.life_max)
        # Calculate the portfolio value considering diminishing returns
        self.portfolio_value = sum(stock.diminishing_value() for stock in self.stocks)

        # Calculate the average portfolio performance
        self.calculate_portfolio_performance()

        # Adjust the impact of the portfolio value and performance
        portfolio_factor = self.portfolio_performance # (self.portfolio_value / 500) + self.portfolio_performance  # Reduced weight

        # Rarity impact (consider reducing the exponent if it's too dominant)
        rarity_factor = self.rarity ** .05  # Adjusted exponent for rarity

        # Final stonks calculation
        self.stonks = (scaled_power + scaled_defense + scaled_life + portfolio_factor) * rarity_factor

    def print_stats(self, prefix=""):
        print(f"{prefix}{self.name} - Life: {self.life}/{self.life_max}, Power: {self.power}, Defense: {self.defense}, "
              f"Stonks: {self.stonks}, Portfolio Value: {self.portfolio_value}, Portfolio Performance: {self.portfolio_performance}")

    def calculate_stats(self):
        rarity_impact = self.rarity ** Broker.RARITY_IMPACT_MOD
        self.calculate_defense(rarity_impact)
        shares_factor = sum(stock.shares_factor() for stock in self.stocks)
        self.calculate_life(shares_factor, rarity_impact)
        self.calculate_power(rarity_impact)
        self.calculate_stonks()

    def perform_battle(self, opponent):
        round_number = 1
        attacking, defending = (self, opponent) if random.random() < 0.5 else (opponent, self)

        while self.life > 0 and opponent.life > 0:
            print(f"Round {round_number}:")
            print(f"  Attacker ({attacking.name}) - Life: {attacking.life}, Power: {attacking.power}, Defense: {attacking.defense}")
            print(f"  Defender ({defending.name}) - Life: {defending.life}, Power: {defending.power}, Defense: {defending.defense}")

            attack_power = random.uniform(*attacking.power)
            damage = max(1, attack_power - defending.defense) if attack_power >= defending.defense else 1
            if damage <= 0 or random.random() < 0.05:
                damage = attacking.average_power - defending.defense if attacking.average_power >= defending.defense else attacking.average_power * .1

            if damage > 0:
                print(f"  {attacking.name} attacks and deals {damage} damage to {defending.name}")
                defending.life -= damage
                if defending.life <= 0:
                    defending.life = 0
                    print(f"{attacking.name} wins the battle!")
                    break
            else:
                print(f"  {attacking.name}'s attack missed.")

            attacking, defending = defending, attacking
            round_number += 1
            print("\n")

# Sample usage
broker1 = Broker(name="Broker 1", rarity=2, initial_stocks=[
    Stock(symbol='AAPL', open_price=150.0, high_price=155.0, low_price=149.0, current_price=152.0, volume=1000000, shares=1557, avg_volume_7d=950000, change_percent='0.0646%')
])

broker2 = Broker(name="Broker 2", rarity=5, initial_stocks=[
    Stock(symbol='AAPL', open_price=150.0, high_price=155.0, low_price=149.0, current_price=152.0, volume=1000000, shares=1, avg_volume_7d=950000, change_percent='0.0646%'),
    Stock(symbol='GOOG', open_price=2500.0, high_price=2550.0, low_price=2490.0, current_price=2530.0, volume=800000, shares=1, avg_volume_7d=780000, change_percent='1.2%'),
    Stock(symbol='TSLA', open_price=650.0, high_price=660.0, low_price=645.0, current_price=655.0, volume=1200000, shares=1, avg_volume_7d=1100000, change_percent='0.75%'),
    Stock(symbol='AMZN', open_price=3200.0, high_price=3250.0, low_price=3190.0, current_price=3240.0, volume=900000, shares=1, avg_volume_7d=850000, change_percent='0.31%')
])

broker1.calculate_stats()
broker2.calculate_stats()
broker1.print_stats("Before Battle - ")
broker2.print_stats("Before Battle - ")
broker1.perform_battle(broker2)
broker1.print_stats("After Battle - ")
broker2.print_stats("After Battle - ")
