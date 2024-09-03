from exercise_3 import Exercise3

EXAMPLE_JSON = 'example.json'

def test_constructor():
    exercise3 = Exercise3(EXAMPLE_JSON)

def test_name():
    exercise3 = Exercise3(EXAMPLE_JSON)
    assert exercise3.get_username() == 'terrance'

def test_time():
    exercise3 = Exercise3(EXAMPLE_JSON)
    assert exercise3.get_time_remaining() == 60
    exercise3.add_hour()
    assert exercise3.get_time_remaining() == 120

def test_items():
    exercise3 = Exercise3(EXAMPLE_JSON)
    assert exercise3.get_items() == ['milk', 'sugar', 'eggs', 'flour']

def test_total():
    exercise3 = Exercise3(EXAMPLE_JSON)
    assert exercise3.get_total() == 10.50
