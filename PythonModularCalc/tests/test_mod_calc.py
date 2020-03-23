from PythonModerateCalc.Calculator import Calculator
import pytest
import unittest


class test_PythonModerateCalc(unittest.TestCase):
    def test_calc(self):
        c = Calculator()
        assert c

    def test_calc_add(self):
        Calculator.clear()
        assert Calculator.add(5) == 5

    def test_calc_subtract(self):
        Calculator.clear()
        assert Calculator.subtract(10) == -10

    def test_calc_multiply(self):
        Calculator.clear()
        assert Calculator.multiply(2) == 0

    def test_calc_divide(self):
        Calculator.clear()
        Calculator.add(5)
        assert Calculator.divide(5) == 1
