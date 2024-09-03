import sqlite3

connection = sqlite3.connect("dosa.db")
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers(
	id INTEGER PRIMARY KEY,
	name CHAR(64) NOT NULL,
	phone CHAR(10) NOT NULL
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS items(
	id INTEGER PRIMARY KEY,
	name CHAR(64) NOT NULL,
	price REAL NOT NULL
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
	id INTEGER PRIMARY KEY,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	cust_id INT NOT NULL,
    notes TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS item_list(
    order_id NOT NULL,
    item_id NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(item_id) REFERENCES items(id)
);
""")

def add_customer(name, phone):
    cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?);",
                   (name, phone))

def list_customers():
    rows = cursor.execute("SELECT id, name, phone FROM customers;").fetchall()
    return rows

def print_customers():
    for customer in list_customers():
        print(f"ID: {customer[0]} Name: {customer[1]} Phone: {customer[2]}")

# add some customers (repeats won't happen if you run this more than once we never save our DB)
add_customer("Ryan", "6095550124")
add_customer("Bill", "6095551024")
add_customer("Divesh", "6095551204")

