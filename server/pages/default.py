import eyearelib.http
import eyearelib.page as page
import eyearelib.logger as logger
import eyearelib.database as db
import plugins, config, sys
from urllib2 import unquote
import json
from twisted.internet import reactor, threads
from os import system, getcwd

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
    needsAuth = False
    needs = ['user', 'pass', 'email', 'read_only']

    def run(self, request, args, output):
        if db.exists('users',{'user': args['user']}) == False:
            # insert into database
            pass
        else:
            output['status'] = 7
            output['payload'] = ["user already exists"]

class Auth(page.Page):
    needsAuth = False
    needs = ['user', 'pass']

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
    class Wait(page.LongRequest):
        needs = ['data']

        def isReady(self, request, args, output):
            query = unquote(args['data'])
            count = db.count('events',json.loads(query))
            logger.d("query = %s\ncount = %s",
                json.loads(query), count)
            return (count > 0)

        def process(self, request, args, output):
            query = unquote(args['data'])
            logger.d("query = %s",json.loads(query))
            output['payload'] =\
                list(db.find('events',json.loads(query)))
            for item in output['payload']:
                try:
                    del item['user']
                except:
                    pass

    def __init__(self):
        page.Page.__init__(self)
        self.putChild('wait', self.Wait())

