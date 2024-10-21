import json
import random
import os


class Guesser():
    def __init__(self):
        print("Welcome to the Guessing Game!")
        
        self.score = 0
        self.tries = 3
        self.level = 1
        self.next_number()
        self.load_state()
    
    def next_number(self):
        max = 9 + ((self.level - 1) * 5)
        max += 1
        print(f"I picked a random number between 1-{max}")
        self.answer = random.randrange(0,max)

    def load_state(self):
        try:
            with open("guesser") as f:
                self.__dict__ = self.__dict__ | json.load(f)
                # print(f"Loaded some fun? {self.__dict__}")
        except Exception as e:
            print(e)

    def save_state(self):
        with open("guesser","+wt") as f:
            # print(f"{json.dumps(self.__dict__)}")
            print(self)
            f.write(json.dumps(self))
    
    def adjust_level(self):
        if self.score < 0:
            self.score = 0
        self.level = (4 + ((self.level - 1) * 5)) + 1 #(self.score % 5)
        # if we don't want level 0
        if self.level < 1:
            self.level = 1
        # (condition)?true:false
        self.level = 1 if self.level<1 else self.level
        print(f"The current level is {self.level}")

    def end_of_level(self):
        self.adjust_level()
        self.next_number()
        self.tries = 3

    def start(self):
        while True:
            
            guess = input("What is it?\n")
            os.system('cls' if os.name == 'nt' else 'clear')
            try:
                guess = int(guess)
                print(f"Guess: {guess} Answer: {self.answer}")
                if guess == self.answer:
                    self.score += 1
                    print(f"You're amazing!\n You now have {self.score} points!")
                    self.end_of_level()
                else:
                    print("You're terrible at this")
                    self.tries -= 1
                    print(f"You have {self.tries} tries remaining")
                    if self.tries <= 0:
                        self.score -= 1
                        print(f"Bad luck, you lost a point and have a score of {self.score}")
                        self.end_of_level()
                self.save_state()
            except ValueError:
                print("Seriously? It's a number game...")
            



guesser = Guesser()
guesser.start()