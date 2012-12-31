"""Base Handler class.
Handlers handle all events from IRC, using a single event() function.
"""
import eyearelib.logger as log
from time import time

CONNECTED = [1, "connected"]
DISCONNECTED = [2, "disconnected"]
JOINED = [3, "joined"]
LEFT = [4, "left"]
QUIT = [5, "quit"]
KICKED = [6, "kicked"]
PERMISSIONS = [7, "permissions"]
ACTION = [8, "action"]
MESSAGE = [9, "message"]
TOPIC = [10, "topic"]
RENAMED = [11, "renamed"]
LOST_CONNECTION = [12, "lost_connection"]
FAILED_CONNECTION = [13, "failed_connection"]
CHANNEL_NICKS = [14, "channel_nicks"]


class Handler:
    def __init__(self):
        log.d("Registered %s for IRC events", self.__class__)

    def _event(self,connection,type,user,server,channel,nicks,data,
    master=True,timestamp=time()):
        try:
            getattr(self, type[1])(connection,user,server,channel,
                nicks,data,master,timestamp)
        except AttributeError:
            self.event(connection,type,user,server,channel,nicks,
                data,master,timestamp)
        finally:
            pass

