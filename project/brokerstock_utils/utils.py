from sql.db import DB
from utils.AlphaVantage import AlphaVantage
from faker import Faker
import random
from brokers.models import Broker
from stocks.models import Stock
def fetch_stocks(symbols):
    symbols = [s.upper().strip() for s in symbols]
    placeholders = ','.join(['%s'] * len(symbols))
    print(f"Symbols: {symbols}")
    print(f"Placeholders: {placeholders}")
    result = DB.selectAll(f"SELECT id, symbol FROM IS601_Stocks WHERE symbol IN ({placeholders})", *tuple(symbols))
    
    stocks = {row['symbol']: row['id'] for row in result.rows} if result.status and result.rows else {}
    print(stocks)
    for symbol in symbols:
        if symbol not in stocks.keys():
            stock_data = AlphaVantage.quote(symbol)
            if stock_data:
                # Assuming stock_data is a dict with correct keys and values
                cols = ', '.join([f"`{k}`" for k in stock_data.keys()])
                placeholders = ', '.join(['%s'] * len(stock_data))
                values = tuple(stock_data.values())
                query = f"INSERT INTO IS601_Stocks ({cols}) VALUES ({placeholders})"
                result = DB.insertOne(query, *values)
                if result.status and result.insert_id:
                    print(f"Successfully inserted stock {symbol}: {stock_data}")
                    stocks[symbol] = result.insert_id

    return [{"id": stock_id, "symbol": symbol} for symbol, stock_id in stocks.items()]



def manage_broker_stocks(broker_id, symbol_data):
    symbols = [s["symbol"] for s in symbol_data]
    stocks = fetch_stocks(symbols)

    # Merge stocks with symbol_data
    merged_stocks = []
    for s in symbol_data:
        stock_info = next((stock for stock in stocks if stock["symbol"] == s["symbol"]), None)
        if stock_info:
            merged_stocks.append({**stock_info, **s})

    # Delete existing associations not in the new list
    stock_symbols = [s['symbol'] for s in merged_stocks]
    delete_placeholders = ','.join(['%s'] * len(stock_symbols))
    DB.delete(f"DELETE FROM IS601_BrokerStocks WHERE broker_id = %s and symbol NOT IN ({delete_placeholders})", *([broker_id] + stock_symbols))

    # Prepare data for bulk insert
    insert_values = {}
    placeholders = []
    for i, stock in enumerate(merged_stocks):
        placeholders.append(f"(%(b{i})s, %(s{i})s, %(sh{i})s)")
        insert_values.update({f"b{i}": broker_id, f"s{i}": stock['symbol'], f"sh{i}": stock['shares']})

    # Bulk insert new associations
    if merged_stocks:
        query = f"INSERT INTO IS601_BrokerStocks (broker_id, symbol, shares) VALUES {','.join(placeholders)} ON DUPLICATE KEY UPDATE shares = VALUES(shares)"
        result = DB.insertOne(query, insert_values)
        if result.status:
            print("Successful mapping of broker to stocks")
        else:
            print("Error occurred during the broker-stock mapping")


def populate_form_with_broker(form, broker):
   # form.process(obj=broker)
    
    form.name.data = broker.name
    form.rarity.data = broker.rarity
    form.life.data = broker.life
    form.power.data = broker.power
    form.defense.data = broker.defense
    form.stonks.data = broker.stonks
    # Clear existing stock entries in the form
    while len(form.stocks.entries) > 0:
        form.stocks.pop_entry()
    for stock in broker.stocks:
        form.stocks.append_entry(stock)
    
    for k,v in form.data.items():
        print(f"{k} - {v}")

def generate_random_broker():
    fake = Faker()
    name = fake.name()
    rarity = random.choices(range(1, 11), weights=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1], k=1)[0]
    broker = Broker(id=None, name=name, rarity=rarity, life=0, power=0, defense=0, stonks=0)
    result = DB.selectAll("SELECT DISTINCT symbol FROM IS601_Stocks")
    stocks = []
    if result.status:
        available_symbols = [row['symbol'] for row in result.rows]
        selected_symbols = random.sample(available_symbols, min(len(available_symbols), rarity))
        placeholders = ",".join(["%s" for x in selected_symbols])
        query = f"""
        SELECT *, 1 as shares FROM IS601_Stocks 
        WHERE symbol in ({placeholders})
        AND IS601_Stocks.latest_trading_day = (
            SELECT MAX(latest_trading_day) FROM IS601_Stocks AS latest_stock
            WHERE latest_stock.symbol = IS601_Stocks.symbol
        )"""
        result = DB.selectAll(query, *selected_symbols)
        if result.status and result.rows:
            print(f"rows: {result.rows}")
            for row in result.rows:
                broker.add_stock(Stock(**row))
    
    broker.recalculate_stats()
    return broker
    
def create_or_update_broker(form, broker_id=None):
    if not broker_id:
        query = "INSERT INTO IS601_Brokers (name, rarity, life, power, defense, stonks) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (form.name.data, form.rarity.data, form.life.data, form.power.data, form.defense.data, form.stonks.data)

        result = DB.insertOne(query, *values)
        broker_id = result.insert_id
    
    stock_symbols = [{"symbol": entry.symbol.data, "shares": entry.shares.data} for entry in form.stocks]
    manage_broker_stocks(broker_id, stock_symbols)
    broker = fetch_broker_data(broker_id)
    
    if broker_id:
        query = "UPDATE IS601_Brokers SET name = %s, rarity = %s, life = %s, power = %s, defense = %s, stonks = %s WHERE id = %s"
        values = (broker.name, broker.rarity, broker.life, broker.power, broker.defense, broker.stonks, broker_id)
        result = DB.update(query, *values)

        
    return result

def fetch_broker_data(broker_id):
    broker = None
    result = DB.selectOne("SELECT b.*, ub.user_id, IF(ub.user_id, 'unavailable', 'available') as status FROM IS601_Brokers b LEFT JOIN IS601_UserBrokers ub on b.id = ub.broker_id WHERE b.id = %s", broker_id)
    if result.status and result.row:
        broker = Broker(**result.row)
        stocks = get_associated_stocks(broker.id)
        for stock in stocks:
            broker.add_stock(stock)
        broker.recalculate_stats()
    else:
        print("Broker not found")
        flash("Broker not found", "danger")
    return broker

def get_associated_stocks(broker_id):
    stocks = []
    stock_associations = DB.selectAll(
        """SELECT IS601_Stocks.*, IS601_BrokerStocks.shares FROM IS601_Stocks 
        JOIN IS601_BrokerStocks ON IS601_Stocks.symbol = IS601_BrokerStocks.symbol 
        WHERE IS601_BrokerStocks.broker_id = %s
        AND IS601_Stocks.latest_trading_day = (
            SELECT MAX(latest_trading_day) FROM IS601_Stocks AS latest_stock
            WHERE latest_stock.symbol = IS601_Stocks.symbol
        )
        """, broker_id
    )
        
    if stock_associations.status:
        stocks = [Stock(**stock) for stock in stock_associations.rows]
    return stocks