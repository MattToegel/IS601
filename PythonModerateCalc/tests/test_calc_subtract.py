
def test_calc_subtract():
	from Calculator import Calculator
	#c = Calculator()
	assert Calculator.subtract(10) == -10

def test_calc_subtract_fail():
	from Calculator import Calculator
	#c = Calculator()
	assert Calculator.subtract(10) != 15
