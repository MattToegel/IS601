# [x] Run the application
# [x] Ask for a maximum range (with a hard coded minimum option)
# [x] Generate a random number between 0 and chosen range (with a minimum)
# [x] Save the guess in a file so it can be reloaded later
# [x] Ask the user to guess 5 times per round
# [x] Game ends and resets back to the beginning if all guess expire in the round
# [x] Guessing correctly moves on to the next round
# [x] Next round will increase the range slightly and pick a new number
# [x] number of guesses will be saved to a file
# [x] round will be saved to a file
# [x] allow new game (remove save file)
import random
import os


class NumberGuesser:

    def __init__(self):
        self.max = 10
        self.original_max = 10
        self.guess = None
        self.strikes = 5
        self.round = 0
        self.guesses = 0

    def load_state(self):
        f = None
        try:
            f = open("secret_Data.txt", "r")
            results = f.read()
            if results:
                lines = results.split("\n")
                data = lines[1].split(",")
                self.guess = int(data[0])  # guess
                self.round = int(data[1])  # round
                self.round -= 1  # decrease by 1 due to new_round() logic
                self.guesses = int(data[2])  # guesses
                self.original_max = int(data[3])  # original is stored, we'll use it to calc current max
                # determine current max based on original and round (-1 since round 1 is already the original_max)
                self.max = self.original_max + self.round - 1
                print(f"Loaded Round {self.round + 1} with {self.guesses} total guess")
        except Exception as e:
            # print(e) # typically should be file not found if we choose new game
            pass
        finally:
            try:
                if f is not None:
                    f.close()
            except Exception as e:
                print(e)

    def save_state(self):
        f = open("secret_Data.txt", "w")
        f.writelines(
            ("guess,round,guesses,max\n"
             , f"{self.guess},{self.round},{self.guesses},{self.original_max}"))
        # f.write(f"{self.guess},{self.round},{self.guesses}")
        f.close()
        # You can comment this out if you don't want to flood the console with messages
        print("Saved game state")

    @staticmethod
    def _is_number(num):
        try:
            int(num)
            return True
        except:
            return False

    def new_round(self, is_reset=False):
        if is_reset:
            # round goes back to 1, max resets to original, guesses reset, and strikes reset
            self.round = 1
            self.max = self.original_max + 1
            self.guesses = 0
        else:
            # increase round, increase range (can change the max += 1 to whatever increment you want)
            self.round += 1
            self.max += 1
        print(f"You're on round {self.round}")
        # update random value only if we didn't load one from the save file
        # or if we're resetting any game state, pick a new guess if our guess is out of range
        if self.guess is None or self.guess > self.max:
            self.guess = random.randrange(0, self.max + 1)
            print(f"I picked a number between 0 and {self.max}, can you guess what it is?")
        else:  # Just so we know it loaded from the file correctly without giving away any hints
            print(f"I previously picked a number between 0 and {self.max}, can you guess what it is?")
        # reset number of strikes
        self.strikes = 5

    def new_game(self):
        max_value = input("What maximum value do you want to start with?")
        if NumberGuesser._is_number(max_value):
            max_value = int(max_value)
            if max_value < 5:
                max_value = 5
                print("Maximum range must be 5 or greater")
        else:
            print("Invalid number, good bye")
            exit(2)
        # subtracting 1 since new_round() adds 1 if it's not being reset
        self.max = max_value - 1
        self.original_max = self.max

    def run(self):
        try:
            self.load_state()
            while True:
                # case for user choosing "new game" or if it's a fresh start
                if self.round < 1:
                    self.new_game()
                    self.new_round()
                user_guess = input("Your guess:")
                if NumberGuesser._is_number(user_guess):
                    self.guesses += 1
                    if int(user_guess) == self.guess:
                        print("Wow you guess it correctly!")
                        self.guess = None  # reset it due to updated logic in new_round()
                        self.new_round()
                    else:

                        self.strikes -= 1
                        print(f"Sorry that's wrong try again. Attempts remaining {self.strikes}/5")
                        if self.strikes < 1:
                            print("You ran out of tries, please play again")
                            self.new_round(is_reset=True)
                    self.save_state()  # for now this should be fine, it's not super expensive to open/save each round
                    # since it's once every few seconds. If the game loop were more frequent, then another location would be best
                else:
                    if user_guess == "quit":
                        print("Thanks for playing, good bye")
                        exit(0)
                    elif user_guess == "new game":
                        try:
                            os.remove("secret_Data.txt")
                        except Exception as e:
                            print(e)
                        self.round = 0  # triggers the prompt to ask for initial max range
                        print("Reset saved data")
                    else:
                        print("Sorry, you can only guess numbers")
        except Exception as e:
            print(e)
        # self.save_state() # may not be a good idea to save state always at the end, we can lose important info if user immediately quits


if __name__ == '__main__':
    game = NumberGuesser()
    game.run()
