import random
import math
from triangle_class import Triangle  # Correct import for the Triangle class

base = random.randint(1, 10)
height = random.randint(1, 10)

def test_constructor():
    my_triangle = Triangle(base, height)
    assert my_triangle.base == base
    assert my_triangle.height == height

def test_hypotenuse():
    my_triangle = Triangle(base, height)
    assert my_triangle.hypotenuse() == math.sqrt(base**2 + height**2)

def test_area():
    my_triangle = Triangle(base, height)
    assert my_triangle.area() == (1/2) * (base * height)

def test_string_representation_of_a_class():
    my_triangle = Triangle(base, height)
    assert f"{my_triangle}" == f"Triangle: base={base}, height={height}"
