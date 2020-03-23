
def divide(previous_answer, num):
	try:
		previous_answer /= num
		return previous_answer
	except ZeroDivisionError:
		print("divide by zero")