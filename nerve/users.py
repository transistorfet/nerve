#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import hashlib
import threading


class UserLoginError (Exception): pass
class UserPermissionsError (Exception): pass


class login (object):
    def __init__(self, username, password):
        self._username = username
        self._password = password

    def __enter__(self):
        if not Users().login(self._username, self._password):
            raise UserLoginError('invalid username or password (' + self._username + ')')

    def __exit__(self, type, value, traceback):
        Users().logout()

def require_permissions(role):
    if not Users().require_permissions(role):
        raise UserPermissionsError()


# TODO in a way this is really a model, isn't it?  It's not a device, it doesn't have threads or anything stateful...
# A user object itself might be a 'device' or something, but these methods are just basic lib/db functions
# should it actually be a singleton?  The biggest issue, as always, is the fact that command line args need to be parsed first
# in order to get the configdir
class Users (object):
    singleton = None
    user_threads = { }

    def __new__(cls):
        if not cls.singleton:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def __init__(self):
        self.db = nerve.Database('users.sqlite')

        if not self.db.table_exists('roles'):
            self.db.create_table('roles', "id INTEGER PRIMARY KEY, role TEXT, weight NUMERIC")
            self.add_role('admin', 0)
            self.add_role('user', 1)
            self.add_role('guest', 100)

        if not self.db.table_exists('users'):
            self.db.create_table('users', "id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, last_login NUMERIC")
            self.add_user('admin', 'admin', 'admin')
            self.add_user('guest', '', 'guest')

        self.db.create_table('user_data', "username TEXT PRIMARY KEY, dataname TEXT, data TEXT")

    def add_role(self, role, weight):
        self.db.where('role', role)
        results = list(self.db.get('roles'))
        if len(results) > 0:
            return False
        self.db.insert('roles', { 'role' : role, 'weight' : weight })
        return True

    def add_user(self, username, password, role):
        self.db.where('username', username)
        results = list(self.db.get('users'))
        if len(results) > 0:
            return False

        self.db.where('role', role)
        results = list(self.db.get('roles'))
        if len(results) <= 0:
            return False

        self.db.where('username', username)
        self.db.insert('users', { 'username' : username, 'password' : self.hash_password(password), 'role' : role })
        return True

    def login(self, username, password):
        password = self.hash_password(password)
        self.db.where('username', username)
        self.db.where('password', password)
        results = list(self.db.get('users'))
        if len(results) <= 0:
            return False
        self.user_threads[threading.current_thread()] = username
        return True

    def logout(self):
        t = threading.current_thread()
        if t in self.user_threads:
            del self.user_threads[t]

    def thread_owner(self):
        t = threading.current_thread()
        if t in self.user_threads:
            return self.user_threads[t]
        return 'system'

    def thread_count(self):
        return len(self.user_threads)

    def require_permissions(self, role):
        t = threading.current_thread()
        if t not in self.user_threads:
            return False
        username = self.user_threads[t]
        results = list(self.db.query("SELECT users.username, users.role, roles.role, roles.weight FROM users, roles WHERE users.username == ? AND users.role == roles.role AND roles.weight <= 0", (username,)))
        if len(results) > 0:
            return True
        return False

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(bytes(password, 'utf-8')).hexdigest()


