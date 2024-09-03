import dosa
import random

def test_count_customers():
    count = 3
    for i in range(0, random.randint(0, 10)):
        dosa.add_customer(str(i), str(i))
        count += 1
    assert dosa.count_customers() == count
