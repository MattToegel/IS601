class Add(Answer):

	@classmethod
	def add (cls, num):
		cls.answer += num
		return round(cls.answer,6)
