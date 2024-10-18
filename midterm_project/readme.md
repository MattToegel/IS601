Midterm Project - Restaurant Order Processing

Project Overview

This project automates the processing of restaurant orders for a Dosa restaurant. The owner has been manually tracking orders, and this project helps by reading the orders from a JSON file and generating two output JSON files for easier management of customer and item data.

The project focuses on generating:

customers.json: A JSON file containing customer phone numbers as keys and their names as values.
items.json: A JSON file containing item names as keys, with their price and the number of times they were ordered.
How the Project is Designed
Input JSON:
The input is a JSON file (example_orders.json) containing a list of orders, where each order includes:

Phone number of the customer.
Customer name.
Items ordered: Each item includes the item name, price, and quantity ordered.
Output Files:
customers.json:
Contains a dictionary where phone numbers are the keys, and the corresponding customer names are the values.
items.json:
Contains a dictionary where each item name is a key. The value is a dictionary containing:
price: The price of the item.
orders: The total number of times the item has been ordered.
Python Script (midterm_project.py):
The Python script processes the input orders, creates the two JSON output files, and ensures that customer data and item data are stored efficiently.

Prerequisites

Python: Ensure you have Python 3.x installed. Run:

bash

python3 --version
If you need to install Python, download it from python.org.

Git: Ensure Git is installed for version control. Check by running:

bash

git --version
Virtual Environment: It is recommended to create a virtual environment to manage dependencies (optional but helpful).

Create and activate a virtual environment:

bash

python3 -m venv venv
source venv/bin/activate
How to Run the Project
Clone the repository to your local machine or ensure the project files are in your working directory.

Ensure the required files (midterm_project.py, example_orders.json) are in place.

Run the following command in the terminal to execute the script:

bash

python3 midterm_project.py example_orders.json
After running, the script will generate two files: customers.json and items.json in the same directory.

Example Input and Output
Input (example_orders.json):
json

[
    {
        "phone": "609-555-0124",
        "name": "Karl",
        "items": [
            {
                "name": "Butter Masala Dosa",
                "price": 12.95,
                "quantity": 2
            }
        ]
    }
]
Output 1 (customers.json):
json

{
    "609-555-0124": "Karl"
}
Output 2 (items.json):
json

{
    "Butter Masala Dosa": {
        "price": 12.95,
        "orders": 2
    }
}
Running Tests
This project includes the option to test the script using pytest. To run the tests:

Ensure you are in the virtual environment (if you set one up).

Install pytest:

bash

pip install pytest
Run the tests:

bash

pytest
Git Branching Strategy
This project follows a branching strategy where all work related to the midterm project is done on the MidtermProject branch. This ensures that the main branch remains clean, and each significant feature or update is committed separately to demonstrate progress.

Future Improvements
Potential enhancements for this project:

Data Validation: Adding checks for the correct formatting of phone numbers, item prices, and quantities.
Error Handling: Managing cases where the input file is invalid or incomplete.
Reporting: Generating additional output files that summarize sales, popular items, or most frequent customers.
