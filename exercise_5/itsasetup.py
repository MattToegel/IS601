set_1 = {0, 2, 4, 6}
set_2 = {1, 2, 3, 4, 5, 6}

set_1.add(8)
print(set_1)

set_1.add(8)
print(set_1)

set_1.remove(8)
print(set_1)

print(set_1 & set_2)
print(set_1 | set_2)
print(set_2 - set_1)