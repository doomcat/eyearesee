"""Permissions fields for users.
Permissions fields are a 4-bit integer, and permissions are applied/checked
for using bitmasks.
"""

ADMIN = 0b1000 # ability to run admin commands on the server
WRITE = 0b0010 # ability to send messages on IRC
LOGIN = 0b0001 # ability to authenticate (useful for temporarily banning)
