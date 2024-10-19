# Midterm Project - Restaurant Order Processing

## Project Overview
This project automates the processing of restaurant orders for a Dosa restaurant. The owner has been manually tracking orders, and this project helps by reading the orders from a JSON file and generating two output JSON files for easier management of customer and item data.

## The Project Focuses on Generating:
- **customers.json**: A JSON file containing customer phone numbers as keys and their names as values.
- **items.json**: A JSON file containing item names as keys, with their price and the number of times they were ordered.

### How the Project is Designed
**Input JSON**:  
The input is a JSON file (`example_orders.json`) containing a list of orders, where each order includes:
- Phone number of the customer.
- Customer name.
- Items ordered: Each item includes the item name, price, and quantity ordered.

### Output Files:
- **customers.json**:  
  Contains a dictionary where phone numbers are the keys, and the corresponding customer names are the values.

- **items.json**:  
  Contains a dictionary where each item name is a key. The value is a dictionary containing:
  - `price`: The price of the item.
  - `orders`: The total number of times the item has been ordered.

## Python Script (`midterm_project.py`)
The Python script processes the input orders, creates the two JSON output files, and ensures that customer data and item data are stored efficiently.

## Prerequisites
- **Python**: Ensure you have Python 3.x installed. Run:
    ```bash
    python3 --version
    ```
    If you need to install Python, download it from [python.org](https://python.org).

- **Git**: Ensure Git is installed for version control. Check by running:
    ```bash
    git --version
    ```

- **Virtual Environment**: It is recommended to create a virtual environment to manage dependencies (optional but helpful).

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
