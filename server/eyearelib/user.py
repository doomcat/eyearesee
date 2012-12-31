"""User class"""
import eyearelib.permissions as permissions
from passlib.apps import custom_app_context as pwd_context
from time import time

salt_format = "{user}|{pass}"

def has_permission(user,permission):
	return (self.permissions & permission) == permission

def is_admin(user):
	return has_permission(user,permissions.ADMIN)

def can_write(user):
	return has_permission(user,permissions.WRITE)

def can_read(user):
	return has_permission(user,permissions.LOGIN)

def hash(user,password):
	return pwd_context.encrypt(salt_format.format(user,password))

def token(user):
	return hash(user,str(time()))

def is_auth(user,password,hashed):
	return hashed == hash(user,password)
