
def test_calc_subtract():
	from Calculator import Calculator
	c = Calculator()
	assert c.subtract(10,5) == 5

def test_calc_subtract_fail():
	from Calculator import Calculator
	c = Calculator()
	assert c.subtract(10,5) != 15
