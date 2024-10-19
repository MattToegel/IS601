import json
import sys

# Function to read and process the JSON orders
def process_orders(input_file):
    # Open and read the JSON file
    with open(input_file, 'r') as f:
        orders_data = json.load(f)
    
    # Initialize dictionaries for customers and items
    customers = {}
    items = {}

    # Iterate through each order
    for order in orders_data:
        phone = order['phone']
        name = order['name']
        
        # Add customers to the dictionary
        customers[phone] = name

        # Process each item in the order
        for item in order['items']:
            item_name = item['name']
            price = item['price']

            # Add or update item details in the dictionary
            if item_name in items:
                items[item_name]['orders'] += 1
            else:
                items[item_name] = {'price': price, 'orders': 1}

    # Write the customers dictionary to a new JSON file
    with open('customers.json', 'w') as customers_file:
        json.dump(customers, customers_file, indent=4)

    # Write the items dictionary to a new JSON file
    with open('items.json', 'w') as items_file:
        json.dump(items, items_file, indent=4)

if __name__ == '__main__':
    # Ensure the script is run with a file argument
    if len(sys.argv) != 2:
        print("Usage: python midterm_project.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    process_orders(input_file)
