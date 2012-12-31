from eyearelib import logger, handler, database, page
from time import time
from base64 import urlsafe_b64encode as base64
import datetime

class Handler(handler.Handler):
	def _event(self,connection,type,user,server, channel,nicks,data,
	master=True,timestamp=time()):
		obj = {"type": type[1], "user": user, "server": server,
			"channel": channel, "nicks": nicks, "data": data,
			"time": timestamp }
		for prop in obj.keys():
			if obj[prop] == None:
				del obj[prop]
		if master:
			logger.d("%s", obj)
			database.getInstance().set('events',obj)
		try:
			getattr(self,type[1])(connection,user,server,channel,
				nicks,data,master,timestamp)
		except AttributeError:
			pass
		page.pollWaitingConnections(user)

	def message(self,connection,user,server,channel,nicks,data,master,
			timestamp):
		if not master: return
		nick = nicks[0].split('!')[0]
		tm = datetime.date.fromtimestamp(timestamp).strftime("%H:%M")
		logger.i("[%s|%s] <%s> %s",tm,channel,nick,data)
