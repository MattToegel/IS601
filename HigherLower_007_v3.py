import random


class HigherLower:
    def __init__(self) -> None:
        
        self.score = 0
        self.is_running = True
        self.score_max = 100
        self.score_increment = 10
        self.num_min = 1
        self.num_max = 10
        self.number = random.randint(self.num_min ,self.num_max)
        self.guess = ""
    def start(self):
        # TODO change config stuff if we want
        self.main()
    # Asks for and validates a guess
    def check_guess(self):
        if self.guess not in ["higher", "lower", "quit"]:
            print("Please choose only higher or lower")
            return False
        return True

    def is_quitting(self):
        if self.guess == "quit":
            self.is_running = False
            print("We're all done")
            return True
        return False
    
    def increment_score(self):
        self.score += self.score_increment
        print(f"You're right! Your score is {self.score}")
        if self.score >= self.score_max:
            print("Congrats you won!!! But at what cost?")
            exit()

    def check_win(self, next_number):
        if (self.guess == "higher" and self.number < next_number) \
            or (self.guess == "lower" and self.number > next_number):
            self.increment_score()
        else:
            print("You're wrong :(")
            
        self.number = next_number

    def main(self):
        while self.is_running:
            print(f"The current number is {self.number}")
            while not self.check_guess():
                self.guess = input("Is the next number higher or lower?").strip().lower()
                
            if not self.is_quitting():
                next_number = random.randint(self.num_min ,self.num_max)
                self.check_win(next_number)
            
if __name__ == "__main__":
    hl = HigherLower()
    print(hl.__dict__)
    hl.start()