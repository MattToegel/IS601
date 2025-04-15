import json

class Exercise3:
    def __init__(self, file_name):
        # Open and load the JSON file
        with open(file_name, 'r') as file:
            self.data = json.load(file)

    def get_username(self):
        return self.data['username']

    def get_time_remaining(self):
        return self.data['time_remaining']

    def add_hour(self):
        # Add 60 minutes to time_remaining
        self.data['time_remaining'] += 60

    def get_items(self):
        # Return list of items in shopping cart
        return list(self.data['shopping_cart'].keys())

    def get_total(self):
        # Calculate and return the total cost of items in shopping cart
        return sum(self.data['shopping_cart'].values())
