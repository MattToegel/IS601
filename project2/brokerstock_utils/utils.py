from sql.db import DB
from utils.AlphaVantage import AlphaVantage
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
