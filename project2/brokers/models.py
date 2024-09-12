from datetime import datetime
from typing import List
from common.utils import JsonSerializable
from stocks.models import Stock  # Replace with the actual path to your Stock class
from decimal import Decimal

class Broker(JsonSerializable):
    def __init__(self,id:int, name: str, rarity: int, life: int, power: int, 
                 defense: int, stonks: int, created: datetime = None, 
                 modified: datetime = None, stocks: List[Stock] = None):
        self.id = id
        self.name = name
        self.rarity = int(rarity)
        self.life = int(life)
        self.life_max = self.life
        self.power = int(power)
        self.defense = int(defense)
        self.stonks = int(stonks)
        self.created = created
        self.modified = modified
        self.stocks = stocks if stocks is not None else []
    def total_value(self):
        return sum(stock.price*stock.shares for stock in self.stocks)
    def add_stock(self, stock: Stock):
        self.stocks.append(stock)
    def recalculate_stats(self):
        self.power = round(self._calculate_power())
        self.defense = round(self._calculate_defense())
        self.life = round(self._calculate_life())
        self.life_max = self.life
        self.stonks = round(self._calculate_stonks())

    def _calculate_power(self):
        if not self.stocks:
            return 0
        base_power = sum((stock.price * Broker.diminishing_returns(stock.shares)) / 15 for stock in self.stocks)
        rarity_modifier = Decimal(1.03 ** self.rarity)
        performance_modifier = 1 + sum(stock.performance_score() for stock in self.stocks) / (500 * len(self.stocks)) if self.stocks else 1
        p = base_power * rarity_modifier * performance_modifier
        return max(0,p)

    def _calculate_defense(self):
        total = 0
        """for stock in self.stocks:
            v = stock.volatility()
            print(f"Volitility: {v}")
            v = 1/v
            print(f"V 1/v: {v}")
            dim = Broker.diminishing_returns(stock.shares)
            print(f"Dim shares: {dim}")
            v *= dim
            print(f"vdim: {v}")
            v /= Decimal(.025)
            print(f"v/: {v}")
            total += v
            print(f"subtotal: {total}")"""
        base_defense = Decimal(sum(((1 / stock.volatility()) * Broker.diminishing_returns(stock.shares)) / Decimal(.025) for stock in self.stocks))
        rarity_modifier = Decimal(1.02 ** self.rarity)
        performance_modifier = 1 + sum(stock.performance_score() for stock in self.stocks) / (1 * len(self.stocks)) if self.stocks else 1
        d = base_defense * rarity_modifier
        print(f"defense: {d}")
        print(f"performance mod: {performance_modifier}")
        d += d * performance_modifier
        print(f"defense: {d}")
        return max(0, d)

    def _calculate_life(self):
        base_life = sum((stock.price * Broker.diminishing_returns(stock.shares)) / Decimal(10) for stock in self.stocks)  # Adjusted calculation
        rarity_modifier = Decimal(1.03 ** self.rarity)  # Rarity modifier
        calculated_life = base_life * rarity_modifier
        l = round(calculated_life) if calculated_life > 0 else 1  # Ensure life is at least 1
        return max(0, l)
    @staticmethod
    def diminishing_returns( shares):
        return Decimal(sum(1 / (i + 1)**0.5 for i in range(shares)))

    

    def _calculate_stonks(self):
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