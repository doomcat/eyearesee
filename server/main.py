#!/usr/bin/env python
import config

import sys, traceback
from twisted.internet import reactor
from eyearelib import http, logger, database, irc
from plugins import *

def eyearexception(extype, value, trace):
    logger.e("EXCEPTION:\n%s",
        "\n".join(traceback.format_exception(extype, value, trace)))

def main(argv=None):
    # Set up some custom exception handling; handle exceptions nicely using
    # the logger module
    sys.excepthook = eyearexception
    logger.getInstance().level = config.LOG_LEVEL

    # Set up the HTTP server
    reactor.listenTCP(config.HTTP_PORT, http.getInstance())

    # Reconnect users to their servers & channels
    users = database.get('users',{})
    for user in users:
        if 'servers' in user.keys():
            for server in user['servers']:
                try:
                    addr = server['addr']
                    chans = server['channels']
                    irc.connect(user['user'], addr, chans)
                except irc.UserNotConnected:
                    logger.e("%s couldn't connect to %s",
                    user['user'], server)
                    logger.trace()
    # Start doing MAGIC
    reactor.run()

if __name__=='__main__':
    main()
