import eyearelib.http
import eyearelib.page as page
import eyearelib.logger as logger
import eyearelib.database as db
import plugins, config, sys
from urllib2 import unquote
import json
from twisted.internet import reactor, threads
from os import system, getcwd

class Admin(page.Page):
	needsAdmin = True

	class GitUpdate(page.Page):
		needsAdmin = False
		needsAuth = False
		def run(self, request, args, output):
			if dir(config.GIT_AUTOUPDATE)\
			and config.GIT_AUTOUPDATE == True\
			and dir(config.GIT_REPO):
				logger.i("github repo updated, pulling...")
				system("%s/update-git.sh" % config.GIT_REPO)
				logger.i("called git, reloading...")
				Admin.Reload.All().run(request,args,output)
				output['payload'] = ["reloaded git"]

	class Reload(page.Page):
		class All(page.Page):
			needsAdmin = True
			def run(self, request, args, output):
				Admin.Reload.Config().run(request,args,output)
				Admin.Reload.HTTP().run(request,args,output)
				Admin.Reload.Plugins().run(request,args,output)
				Admin.Reload.IRC().run(request,args,output)

		class HTTP(page.Page):
			needsAdmin = True
			def run(self, request, args, output):
				eyearelib.http.reloadPages()

		class Plugins(page.Page):
			needsAdmin = True
			def run(self, request, args, output):
				reload(plugins)

		class IRC(page.Page):
			needsAdmin = True
			def run(self, request, args, output):
				eyearelib.events.restart()

		class Config(page.Page):
			needsAdmin = True
			def run(self, request, args, output):
				reload(config)

		needsAdmin = True
		def __init__(self):
			page.Page.__init__(self)
			self.putChild('http',self.HTTP())
			self.putChild('plugins',self.Plugins())
			self.putChild('irc',self.IRC())
			self.putChild('config',self.Config())
			self.putChild('all',self.All())

	def run(self, request, args, output):
		output['admin_functions'] = {
			"reload": ["http","irc","plugins","config"],
			"savedb": 1,
			"makeadmin": 1,
			"userban": 1,
			"userdel": 1
		}

	def __init__(self):
		page.Page.__init__(self)
		self.putChild('reload', self.Reload())
		self.putChild('git-update', self.GitUpdate())

