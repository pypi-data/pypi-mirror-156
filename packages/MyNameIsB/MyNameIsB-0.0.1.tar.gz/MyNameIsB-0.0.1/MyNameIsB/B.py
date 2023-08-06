class B:
	"""
	คลาส B คือข้อมูลเกี่ยวกับคนที่ชื่อ B

	Example
	#-------------------------
	B.show_name()
	B.show_youtube()
	B.about()
	B.show_art()
	#-------------------------
	"""
	def __init__(self):
		self.name = 'B'
		self.page = 'https://www.google.com'

	def show_name(self):
		print('Hello my name is {}'.format(self.name))

	def show_youtube(self):
		print('https://www.youtube.com')

	def about(self):
		text = """
		Hello this is me book. i'm a uncle engineer student"""
		print(text)

	def show_art(self):
		text = """
		      )  (
		     (   ) )
		      ) ( (
		    _______)_
		 .-'---------|  
		( C|/\/\/\/\/|
		 '-./\/\/\/\/|
		   '_________'
		    '-------'
		"""
		print(text)

if __name__ == '__main__':
	B = B()
	B.show_name()
	B.show_youtube()
	B.about()
	B.show_art()
