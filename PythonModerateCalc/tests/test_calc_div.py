
def test_calc_divide():
	from Calculator import Calculator
	#c = Calculator()
	Calculator.reset()
	Calculator.add(5)
	assert Calculator.divide(5) == 1
