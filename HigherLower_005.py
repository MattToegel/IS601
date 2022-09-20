import random

choices = [*range(20)]
latest_number = random.choice(choices)
is_running = True
score = 0
score_increment = 1
score_max = 10
while is_running:
    print(f"Your current score is {score}")
    print(f"The current number is {latest_number}...")
    guess = input("Will the next number be higher or lower?")
    print(f"You guessed {guess}")
    next_number = random.choice(choices)
    while is_running and guess in ["higher","lower", "exit"]:
        if (guess == "higher" and next_number > latest_number) \
        or (guess == "lower" and next_number < latest_number):
            print("You're correct!")
            score += score_increment
            if score >= score_max:
                print("You won it all!")
                is_running = False
        elif guess == "exit":
            print("Thanks for playing")
            is_running = False
        else:
            print("Sorry that's not correct")
            
        latest_number = next_number
        break
    else:
        print("Please enter a valid option (higher, lower, exit")
        