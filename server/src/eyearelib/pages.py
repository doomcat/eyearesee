import eyearelib.http
import eyearelib.page as page
import plugins, config, sys
from twisted.internet import reactor, threads

class Admin(page.Page):
	needsAdmin = True

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

class World(page.Page):
	isLeaf = True
	needsAuth = False
	def run(self, request, args, output):
		output['payload'] = ["guten morgens, das welt!!! :))"]

class Connect(page.Page):
	pass

class Disconnect(page.Page):
	pass

class Join(page.Page):
	pass

class Part(page.Page):
	pass

class Register(page.Page):
	pass

class Auth(page.Page):
	pass

class Message(page.Page):
	pass

class Action(page.Page):
	pass

class Nick(page.Page):
	pass

class Permissions(page.Page):
	pass

class Kick(page.Page):
	pass

class Topic(page.Page):
	pass

class Events(page.Page):
	pass

