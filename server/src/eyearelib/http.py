from twisted.web import server, resource
import json, time, sys, inspect
import eyearelib.logger as log
import eyearelib.permissions as perm
import eyearelib.page
import eyearelib.pages

__instance = None

class Root(eyearelib.page.Page):
	isLeaf = False
	needsAuth = False
	needsAdmin = False

	def __init__(self):
		log.d("Creating a new instance of http.Root...")
		eyearelib.page.Page.__init__(self)

	def restart(self):
		reload(eyearelib.pages)
		for name, page in inspect.getmembers(
			eyearelib.pages, inspect.isclass):
			if 'Page' in [obj.__name__ for obj in page.__bases__]:
				self.putChild(name.lower(), page())
				log.d("%s registered at /%s",
					name, name.lower())

def getInstance():
	global __instance
	if __instance == None:
		__instance = newInstance()
	return __instance

def newInstance():
	global __instance
	pages = Root()
	__instance = server.Site(pages)
	__instance.pages = pages
	pages.restart()
	return __instance

def reloadPages():
	log.d("Calling reloadPages()")
	global __instance
	if __instance != None:
		__instance.pages.restart()
