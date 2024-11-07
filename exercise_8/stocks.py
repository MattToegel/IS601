from datetime import date
import requests
from dotenv import load_dotenv
import os
import sqlite3
import traceback
import sys

load_dotenv()
cursor = sqlite3.connect("stocks.db")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Stocks(
           symbol text not null unique,
            open float default 0,
            high float default 0,
               low float default 0,
               price float default 0,
               volume int default 0,
               latest_trading_day date,
               previous_close float default 0,
               change float default 0,
               change_percent float default 0     
)  
               """)
url = "https://alpha-vantage.p.rapidapi.com/query"
API_KEY = os.getenv("API_KEY")

quote = input("What stock do you care about?").upper()

res = cursor.execute("""SELECT *, DATE('now') FROM Stocks WHERE symbol = ? AND latest_trading_day = DATE('now')""",(quote,))
result = res.fetchone()
print(result)
if not result:
    querystring = {"function":"GLOBAL_QUOTE","symbol":quote,"datatype":"json"}

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "alpha-vantage.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    json = response.json()
    data = json["Global Quote"]
    # TODO remove the numbers from the keys
    new_dict = {}
    for key in data:
        fixed_key = key.split(" ", 1)[1].replace(" ", "_")
        new_dict[fixed_key] = data[key].replace("%","")

    print(new_dict)



    try:
        placeholders = [f":{key}" for key in new_dict.keys()]
        
        cursor.execute(f"""INSERT OR REPLACE INTO Stocks (symbol, open, high, low, 
                price, 
                volume,
                    latest_trading_day, previous_close, change, change_percent
                ) VALUES ({",".join(placeholders)})
                
                """, new_dict)
        cursor.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
else:
    print(result)