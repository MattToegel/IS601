test = {"name":"Bob", "age":52}
my_tuple = ("abc", 1, "def", 2, test)

print(my_tuple[3])

one_item_tuple = ("abc",)
print(one_item_tuple)
print(tuple[3].__dict__)
tuple[3].__add__(2)
my_tuple[4]["age"] = 22
print(my_tuple)