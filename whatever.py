#todo break into separate example files
"""my_var = "hi"
print(type(my_var))
my_var = 1
print(type(my_var))
my_var = 1.0
print(type(my_var))
my_var = []
print(type(my_var))
my_var = ()
print(type(my_var))
my_var = False
print(type(my_var))"""

"""a = 0.0
b = 1.0
for x in range(10):
    a += 0.1
    print(a)
print(a == b)
print(a)
print(b)"""

"""import sys
my_int = sys.maxsize
print("orignal")
print(my_int)
my_int += 1
my_int *= sys.maxsize
my_int *= sys.maxsize
my_int *= sys.maxsize
print(my_int)
print(type(my_int))"""

"""x = 21
if x >= 18:
    print("at least 18")
    #x += 2
elif x >= 20:
    print("at least 20")
else:
    print("unhandled value")"""

x = 0
for i in range(5):
    if i % 2 == 0:
        x -= 1
    if x % 2 == 0:
        x -= 1
print("x is")
print(x)