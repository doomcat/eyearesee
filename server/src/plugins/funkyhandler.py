from eyearelib import logger, handler, database
from time import time
from base64 import urlsafe_b64encode as base64

class Handler(handler.Handler):
	def event(self,connection,type,user,server, channel,nicks,data,
	master=True):
		t = time()
		obj = {"type": type[1], "user": user, "server": server,
			"channel": channel, "nicks": nicks, "data": data,
			"time": t }
		for prop in obj.keys():
			if obj[prop] == None:
				del obj[prop]
		logger.d("Event! %s", type[1])
		if master:
			logger.d("%s", obj)
			database.getInstance().set('events',obj)
