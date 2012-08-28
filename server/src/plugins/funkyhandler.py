from eyearelib import logger, handler, database
from time import time
from base64 import urlsafe_b64encode as base64

class Handler(handler.Handler):
	def event(self,connection,type,user,server,channel,nicks,data):
		if type != "message":
			logger.d("%s@%s:%s> %s", nicks, server, channel, data)
		else:
			nick = nicks[0].split('!')[0]
			logger.d("%s|%s: %s",channel,nick,data)
		t = time()
		obj = {"type": type, "user": user, "server": server,
			"channel": channel, "nicks": nicks, "data": data,
			"time": t }
		oid = ''
		for prop in ['type','server','channel', 'nicks', 'data']:
			if obj[prop] != None:
				oid += base64(str(obj[prop]))
		for prop in obj.keys():
			if obj[prop] == None:
				del obj[prop]
		obj["_id"] = oid
		logger.d("%s", obj)
		database.getInstance().set('events',obj)
