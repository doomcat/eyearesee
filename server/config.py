import eyearelib.logger
# Log levels (eyearelib.logger.XXX):
# ERROR     When something serious has occurred, probably causing the
#           server to quit
# WARNING   When an error/exception has been thrown/caught, but the server
#           can continue running
# INFO      Information that's useful to see in logs
# DEBUG     Debug stuff
LOG_LEVEL=eyearelib.logger.DEBUG

URL="https://eyearesee.in/api/" # URL of the HTTP interface
HOSTNAME="eyearesee.in"         # Hostname of your server
HTTP_ADDRESS="0.0.0.0"          # Address to listen for HTTP requests on
HTTP_PORT=8081                  # Port to listen for HTTP requests on
GIT_AUTOUPDATE=True             # Whether to reload pages/config/plugins
                                # when git origin has been updated (and git
                                # hooks called)
GIT_REPO="/root/eyearesee"      # Where the eyearesee repo is on your system

ADMINS=["owain","git"]          # Users who can run /api/admin/... requests
READ_ONLY=["eyearesee","git"]   # Users who can't send messages on IRC
                                # Note: these are just a shortcut for when you
                                # don't want to edit a database. Each user has
                                # a 'permissions' flag in the database which
                                # dictates their access/read/write privileges.

import plugins.funkyhandler
EVENT_HANDLERS=[
    plugins.funkyhandler
]

import plugins.mongodb
DATABASE_HANDLER=plugins.mongodb

# Stuff specific to the mongodb plugin
# Edit these if your mongodb is on a remote server
MONGO_HOST='localhost'
MONGO_PORT=27017
MONGO_DBNAME='eyearesee'

# Make certain users admins or read_only
# (so you don't have to faff around editing the database directly)
# NOTE: This changes the users permissions in the database itself too.
import eyearelib.database as db
import eyearelib.permissions as permissions

for user in ADMINS:
    u = db.get('users',{'user': user})
    if len(u) > 0:
        u = u[0]
        eyearelib.logger.i("Making %s an admin",user)
        u['permissions'] = u['permissions']|permissions.ADMIN
        db.set('users',u)

for user in READ_ONLY:
    u = db.get('users',{'user': user})
    if len(u) > 0:
        u = u[0]
        eyearelib.logger.i("Making %s a read-only user",user)
        u['permissions'] = u['permissions']|(not permissions.WRITE)
        db.set('users',u)

