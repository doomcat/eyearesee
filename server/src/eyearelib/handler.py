"""Base Handler class.
Handlers handle all events from IRC, using a single event() function.
"""
import eyearelib.logger as log

CONNECTED = 1
DISCONNECTED = 2
JOINED = 3
LEFT = 4
QUIT = 5
KICKED = 6
PERMISSIONS = 7
ACTION = 8
MESSAGE = 9
TOPIC = 10
RENAMED = 11
LOST_CONNECTION = 12
FAILED_CONNECTION = 13


class Handler:
	def __init__(self):
		log.d("Registered %s for IRC events", self.__class__)

	def event(self,connection,type,user,server,channel,nicks,data):
		pass

