import math

class Triangle:
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def hypotenuse(self):
        """Calculate the hypotenuse of the triangle using the Pythagorean theorem."""
        return math.sqrt(self.base**2 + self.height**2)

    def area(self):
        """Calculate the area of the triangle."""
        return (1/2) * (self.base * self.height)

    def __str__(self):
        """Return a string representation of the triangle."""
        return f"Triangle: base={self.base}, height={self.height}"
