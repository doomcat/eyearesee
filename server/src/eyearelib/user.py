"""User class"""
import eyearelib.permissions as permissions

class User:
	def __init__(self):
		self.token = None
		self.hash = None
		self.permissions = permissions.WRITE
		self.servers = []

	def has_permission(self,permission):
		return (self.permissions & permission) == permission
