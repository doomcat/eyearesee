from twisted.web import server, resource
from twisted.web.server import NOT_DONE_YET
import json, time, sys, inspect
import eyearelib.logger as log
import eyearelib.permissions as perm
import eyearelib.page
import eyearelib.database as db
import pkgutil
import pages
from urllib2 import unquote

__instance = None
__openConnections = {}

class Root(eyearelib.page.Page):
    isLeaf = False
    needsAuth = False
    needsAdmin = False

    def run(self,request,args,output):
        if 'uri' in args.keys():
            request.redirect('./%s' % unquote(args['uri']))
            request.finish()

    def __init__(self):
        log.d("Creating a new instance of http.Root...")
        eyearelib.page.Page.__init__(self)

    def registerModule(self, module):
        for name, page in inspect.getmembers(module, inspect.isclass):
            if 'Page' in [obj.__name__ for obj in page.__bases__]:
                self.putChild(name.lower(), page())
                log.d("%s registered at /%s",name,name.lower())

    def restart(self):
        reload(pages)
        for mname in pages.__all__:
            exec "import pages.%s" % mname
            exec "reload(pages.%s)" % mname
            exec "eyearelib.http.getInstance().pages"\
                +".registerModule(pages.%s)" % mname

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
