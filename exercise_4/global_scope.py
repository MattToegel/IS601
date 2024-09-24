my_global_variable = 42

def print_answer():
    global my_global_variable
    print(my_global_variable)
    my_global_variable += 1

print_answer()

print_answer()