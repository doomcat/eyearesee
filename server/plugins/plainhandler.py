import eyearelib.logger as log
import eyearelib.handler as handler


class Handler(handler.Handler):
    def event(self, type, user, server, channel, nicks, data):
        #log.d("%s@%s:%s> %s", nicks, server, channel, data)
        log.d("%s", data)
