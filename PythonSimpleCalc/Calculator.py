class Calculator:
	def add(self, num1, num2):
		return num1 + num2

	def subtract(self, num1, num2):
		return num1 - num2

	def multiply(self, num1, num2):
		return num1 * num2

	def divide(self, num1, num2):
		return num1 / num2


if __name__ == "__main__":
	c = Calculator()
	print (c.add(1,2))
