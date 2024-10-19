import json
import sys
from collections import defaultdict

def read_json(file_path):
    # Reads the orders JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def create_customers_json(orders):
    # Creates customers.json from orders
    customers = {}
    for order in orders:
        phone = order['phone']  # Extract phone number
        name = order['name']  # Extract customer name
        customers[phone] = name
    
    with open('customers.json', 'w') as file:
        json.dump(customers, file, indent=4)

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
    
    with open('items.json', 'w') as file:
        json.dump(items, file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <orders_file>")
        sys.exit(1)
    
    file_name = sys.argv[1]
    orders = read_json(file_name)
    create_customers_json(orders)
    create_items_json(orders)
    print("Customers and items data successfully written.")
