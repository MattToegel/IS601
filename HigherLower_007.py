import random


number = random.randint(1,100)
score = 0
is_running = True
score_max = 100
score_increment = 1
num_min = 1
num_max = 10
while is_running:
    
    
    print(f"The current number is {number}")
    guess = input("Is the next number higher or lower?").strip().lower()
    next_number = random.randint(num_min ,num_max)
    while is_running and guess in ["higher","lower", "quit"]:
        if (guess == "higher" and number < next_number) \
        or (guess == "lower" and number > next_number):
            
            score += score_increment
            print(f"You're right! Your score is {score}")
            if score >= score_max:
                print("Congrats you won!!! But at what cost?")
                exit()
        elif guess == "quit":
            is_running = False
            print("We're all done")
            break
        else:
            print("You're wrong :(")
        number = next_number
        break
    else:
        print("Please choose only higher or lower")
    
    