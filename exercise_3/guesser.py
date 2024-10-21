import random
import os


class Guesser():
    def __init__(self):
        print("Welcome to the Guessing Game!")
        
        self.score = 0
        self.tries = 3
        self.level = 1
        self.next_number()

    def next_number(self):
        print("I picked a random number between 1-10")
        max = 10
        match(self.level):
            
            case 2:
                max = 15
            case 3:
                max = 20
            case 4:
                max = 25
            case 5:
                max = 30
            case _:
                max = 5
                

        self.answer = random.randrange(0,max)
    
    def adjust_level(self):
        self.level = (self.score % 5)
        print(f"The current level is {self.level}")

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
                    self.adjust_level()
                    self.next_number()
                else:
                    print("You're terrible at this")
                    self.tries -= 1
                    print(f"You have {self.tries} tries remaining")
                    if self.tries <= 0:
                        self.score -= 1
                        
                        print(f"Bad luck, you lost a point and have a score of {self.score}")
                        self.adjust_level()
                        self.tries = 3
                        self.next_number()
                        

                    
            except ValueError:
                print("Seriously? It's a number game...")
            



guesser = Guesser()
guesser.start()