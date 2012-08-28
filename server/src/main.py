#!/usr/bin/python -OO
import config

import sys, traceback
from twisted.internet import reactor
from eyearelib import http, logger, database, irc
from plugins import *

def eyearexception(extype, value, trace):
	logger.e("EXCEPTION:\n%s",
		"\n".join(traceback.format_exception(extype, value, trace)))
sys.excepthook = eyearexception

logger.getInstance().level = config.LOG_LEVEL
reactor.listenTCP(config.HTTP_PORT, http.getInstance())
irc.connect("owain","irc.aberwiki.org:6667")
irc.connect("eyearesee","irc.aberwiki.org:6667")
try:
	irc.getConnection("owain","irc.freenode.net:6667")
except irc.UserNotConnected:
	logger.e("Not connected")
reactor.run()
