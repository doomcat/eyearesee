from twisted.web import server, resource
import json, time
import eyearelib.logger as log
import eyearelib.permissions as perm
import eyearelib.database as database

def sanitize(request):
	args = {}
	for arg in request.args:
		args[str(arg)] = str(request.args[arg][0])
	return args

def exists(args, key):
	if key not in args.keys(): return False
	if args[key] in ['None', '']: return False
	return True

class Page(resource.Resource):
	isLeaf = False
	needsAuth = True
	needsAdmin = False

	def __init__(self):
		resource.Resource.__init__(self)

	def render_GET(self, request):
		args = sanitize(request)
		request.setHeader("content-type", "application/json")
		return self.validate(request, args)
		
	render_POST = render_GET	

	def validate(self, request, args):
		self.database = database.getInstance()
		output = {'status': 1, 'server_time': time.time()}
		dont_run = False
		if self.needsAuth is True:
			test = self.database.get('users',
				{'user': args['user']})[0]
			if not exists(args, 'user')\
			or not exists(args, 'token'):
				output['status'] = 2
				dont_run = True
			elif test['token'] != args['token']:
				output['status'] = 3
				dont_run = True
			elif self.needsAdmin is True\
			and (test['permissions'] & perm.ADMIN) != perm.ADMIN:
				output['status'] = 4
				dont_run = True
		try:
			if dont_run is False:
				self.run(request, args, output)
		except:
			log.trace()
			output['status'] = -1
		
		return json.dumps(output, indent=2)		

	def run(self, request, args, output):
		output['payload'] = ["default Page does nothing"]
