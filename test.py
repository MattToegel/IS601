import sys

a = sys.maxsize
print("a is " + str(a) + " " + str(type(a)))
a += sys.maxsize
print("a is " + str(a) + " " + str(type(a)))

