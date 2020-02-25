
def test_calc_add():
	from Calculator import Calculator
	Calculator.reset()
	assert Calculator.add(5) == 5
