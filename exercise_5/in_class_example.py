from datetime import datetime
class DateHelper():
    def __init__(self) -> None:
        self.choice = None
        self.choices = {
            1: {
            "fun": self.choice_1,
            "label":"Days between two dates"
            },
            2:{
                "fun":self.choice_2,
                "label": "Next leap year from date"
            },
            10: {
                "fun": exit,
                "label": "Exit/Quit"
            }}
        while True:
            self.ask_choice()
            self.run_current_choice()
    def run_current_choice(self):
        my_fun = self.choices[self.choice]["fun"]
        my_fun()
    def get_date(self):
        
        while True:
            d = input(f"Please enter date with format (YYYY/DD_MM)")
            try:
                actual_date = datetime.strptime(d, "%Y/%d_%m")
                print(actual_date)
                return actual_date
            except:
                print("WRONG! IT must be YYYY/DD_MM")
            
    
    def choice_1(self):
        """ Prints the number of days between two dates"""
        print("Doing choice 1")
        dates = []
        while len(dates) < 2:
            print(f"Enter Date {len(dates)+1}")
            d = self.get_date()
            dates.append(d)
        print("Ready!")
        days_between = abs(dates[0] - dates[1])
        print(days_between.days)
    def choice_2(self):
        date = self.get_date()
        year = date.year
        while year % 4 != 0:
            year += 1
        print(f" Next Leap Year is {year}")
        pass
        
    def is_valid_choice(self, incoming_choice):
        return incoming_choice in self.choices.keys()
    
    def handle_choice(self):
        if self.choice == 1:
            pass
        elif self.choice == 2:
            pass
    def ask_choice(self):
        while True:
            print("Choose an option")
            for key, value in self.choices.items():
                print(f"Option {key} - {value["label"]}")
            choice = input()
            try:
                choice = int(choice)
                if self.is_valid_choice(choice):
                    self.choice = choice
                    break
            except:
                print("That wasn't valid")
                self.choice = None
DateHelper()