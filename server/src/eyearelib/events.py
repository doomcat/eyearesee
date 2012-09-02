import config
import eyearelib.logger as log
import eyearelib.handler

__instances = []

def getInstances():
	global __instances
	if __instances == []:
		for module in config.EVENT_HANDLERS:
			reload(module)
			__instances.append(module.Handler())
		log.d("Creating new instances of event handlers")
	return __instances

def restart():
	reload(config)
	reload(eyearelib.handler)
	global __instances
	__instances = []

def event(connection=None, type=None, user=None, server=None, channel=None,
	nicks=None, data=None, master=True):
	for handler in getInstances():
		handler.event(connection, type, user,
			server, channel, nicks, data, master)

