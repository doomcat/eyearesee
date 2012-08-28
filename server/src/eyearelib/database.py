import config
from eyearelib import logger as log

__instance = None

def getInstance():
	global __instance
	if __instance is None:
		log.d("Creating a new instance of %s",
			config.DATABASE_HANDLER.__name__)
		__instance = config.DATABASE_HANDLER.Database()
	return __instance

def restart():
	reload(config)
	global __instance
	__instance = None

def get(collection, query):
	getInstance().get(collection, query)

def set(collection, query):
	getInstance().set(collection, query)

