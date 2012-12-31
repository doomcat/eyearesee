"""Logger class.
Singleton class that handles logging."""

from sys import stdout, stderr
import traceback, time, config

ERROR = 4
WARNING = 3
INFO = 2
DEBUG = 1
SPAM = 0

__instance = None

def getInstance():
	global __instance
	if __instance is None:
		__instance = Logger()
	return __instance

def d(message, *variables):
	getInstance().write(DEBUG, message, variables)

def i(message, *variables):
	getInstance().write(INFO, message, variables)

def w(message, *variables):
	getInstance().write(WARNING, message, variables)

def e(message, *variables):
	getInstance().write(ERROR, message, variables)

def spam(message, *variables):
	getInstance().write(SPAM, message, variables)

def trace():
	getInstance().write(ERROR, "%s", (traceback.format_exc()))	

class Logger:
	def __init__(self, output=stdout, error=stderr, level=DEBUG):
		self.output = output
		self.error = error
		self.level = level

	def write(self, level, message, variables):
		if level < self.level: return
		if level == ERROR or level == WARNING:
			output = self.error
		else:
			output = self.output
		prefix = str(level)+'|'+str(int(time.time()))+': '
		string = message % variables
		string = string.replace("\t","  ")
		length = len(prefix)
		i = length
		startOfLine = True
		lineStart = 0
		output.write(prefix)
		for char in string:
			if char == "\n":
				lineStart = 0
				startOfLine = True
			if i > 78 or char == "\n":
				output.write("\n")
				output.write("  ")
				i = 2
			if char == " ":
				if startOfLine == True:
					lineStart += 1
			else:
				startOfLine = False
			if char != "\n":
				output.write(char)
				i += 1
		output.write("\n")

