import random


class HigherLower:
    def __init__(self) -> None:
        self.choices = [*range(20)]
        self.latest_number = random.choice(self.choices)
        self.is_running = True
        self.score = 0
        self.score_increment = 10
        self.score_max = 100

    def start(self):
        self.__run()

    # no need to test right now
    def check_input(self):
        guess = input("Will the next number be higher or lower?").strip().lower()
        if guess in ["higher","lower", "exit"]:
            return guess
        print("Please enter a valid option (higher, lower, exit)")
        return self.check_input()
        #self.check_input()

    def _check_answer(self, guess, next_number):
        
        is_correct = (guess == "higher" and next_number > self.latest_number) \
                or (guess == "lower" and next_number < self.latest_number)
        self.latest_number = next_number
        return is_correct
    
    def _check_score(self, is_correct):
        if is_correct:
            print("You're correct!")
            self.score += self.score_increment
            if self.score >= self.score_max:
                print("You won it all!")
                exit()
        else:
            print("Sorry that's not correct")
    # the __ makes it "private" so not accessible outside of the class
    def __run(self):
        while self.is_running:
            print(f"Your current score is {self.score}")
            print(f"The current number is {self.latest_number}...")
            guess = self.check_input()
            print(f"You guessed {guess}")
            if guess == "exit":
                break
            next_number = random.choice(self.choices)
            is_correct = self._check_answer(guess, next_number)
            self._check_score(is_correct)



if __name__ == '__main__':
    hl = HigherLower()
    print(hl.__dict__)
    hl.start()