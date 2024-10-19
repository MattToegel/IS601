import json
import sys
from collections import defaultdict

def read_json(file_path):
    # Reads the orders JSON file and handles potential file errors
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'.")
        sys.exit(1)

def create_customers_json(orders):
    # Creates customers.json from orders
    customers = {}
    for order in orders:
        phone = order['phone']
        name = order['name']
        customers[phone] = name
    
    try:
        with open('customers.json', 'w') as file:
            json.dump(customers, file, indent=4)
    except IOError:
        print("Error: Unable to write to customers.json")
        sys.exit(1)

def create_items_json(orders):
    # Creates items.json with item names, prices, and the number of times ordered
    items = defaultdict(lambda: {'price': 0, 'orders': 0})
    for order in orders:
        for item in order['items']:
            item_name = item['name']
            item_price = item['price']
            if items[item_name]['orders'] == 0:
                items[item_name]['price'] = item_price
            items[item_name]['orders'] += 1
    
    try:
        with open('items.json', 'w') as file:
            json.dump(items, file, indent=4)
    except IOError:
        print("Error: Unable to write to items.json")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <orders_file>")
        sys.exit(1)
    
    file_name = sys.argv[1]
    orders = read_json(file_name)
    create_customers_json(orders)
    create_items_json(orders)
    print("Customers and items data successfully written.")
