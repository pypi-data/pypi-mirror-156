from colorama import Fore, Back, Style
from colorama import init
from random import randint
import pyttsx3 as pyt
from gtts import gTTS

class APP:


	def calculator(self):
		# use Colorama to make Termcolor work on Windows tooi
		init()
		print( Back.RED )
		print( Fore.BLACK )

		print("работуют только +, -, *, / ")
		print( Back.YELLOW )
		self.c = input("знак: ")
		self.x = float(input("1 цифра: "))
		self.y = float(input("2 цифра: "))
		

		#дуйствие
		if self.c == '+':
			self.r = self.x + self.y
			print(self.r)

		elif self.c == '-':
			self.r = self.x - self.y
			print(self.r)

		elif self.c == '*':
			self.r = self.x * self.y
			print(self.r)

		elif self.c == '/':
			self.r = self.x / self.y
			print(self.r)

		else:
			print("выбрана не верная операция")
			return


	def randoma(self, own, twe):
		self.my_own = own
		self.my_twe = twe

		rand = randint(self.my_own, self.my_twe)

		print(rand)

	
			





class talk():

	def __init__(self, path):
		self.engine = pyt.init()

		with open(path, 'r') as file:
			self.file = file.read()


	def say(self):
		self.engine.say(self.file)
		self.engine.runAndWait()


class help():
	def help(self):
		print("talk(say)\nAPP(randoma)\nAPP(calculator)")
		
