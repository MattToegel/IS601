a = {
    "name": "bob",
    "something":"fun",
    "age":50,
    "hobbies": {"skiing":True,"snowboarding":True}
}

b = {
    "name": "john",
    "age":24,
    "hobbies":{"knitting":True}
}

print(a)
print(b)
c = a | b
print(c)