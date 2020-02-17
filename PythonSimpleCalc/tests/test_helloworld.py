import pytest

def test_helloworld():
	"""My first test"""
	from helloworld import Helloworld
	h = Helloworld()
	assert h.sayhello() == "hello world"
