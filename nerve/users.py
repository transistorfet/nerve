#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import hashlib
import threading


class UserLoginError (Exception): pass
class UserPermissionsError (Exception): pass
class UserPermissionsRequired (Exception): pass


_user_db = None
_user_threads = { }

def init():
    global _user_db
    _user_db = nerve.Database('users.sqlite')

    if not _user_db.table_exists('roles'):
        _user_db.create_table('roles', "id INTEGER PRIMARY KEY, role TEXT, weight NUMERIC")
        add_role('admin', 0)
        add_role('user', 1)
        add_role('guest', 100)

    if not _user_db.table_exists('users'):
        _user_db.create_table('users', "id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, last_login NUMERIC")
        add_user('admin', 'admin', 'admin')
        add_user('guest', '', 'guest')

    _user_db.create_table('user_data', "username TEXT PRIMARY KEY, dataname TEXT, data TEXT")


def add_role(role, weight):
    _user_db.where('role', role)
    results = list(_user_db.get('roles'))
    if len(results) > 0:
        return False
    _user_db.insert('roles', { 'role' : role, 'weight' : weight })
    return True


def add_user(username, password, role):
    _user_db.where('username', username)
    results = list(_user_db.get('users'))
    if len(results) > 0:
        return False

    _user_db.where('role', role)
    results = list(_user_db.get('roles'))
    if len(results) <= 0:
        return False

    _user_db.where('username', username)
    _user_db.insert('users', { 'username' : username, 'password' : hash_password(password), 'role' : role })
    return True


class login (object):
    def __init__(self, username, password):
        self._username = username
        self._password = password

    def __enter__(self):
        if not _login(self._username, self._password):
            raise UserLoginError('invalid username or password (' + self._username + ')')

    def __exit__(self, type, value, traceback):
        _logout()


def _login(username, password):
    password = hash_password(password)
    _user_db.where('username', username)
    _user_db.where('password', password)
    results = list(_user_db.get('users'))
    if len(results) <= 0:
        return False
    _user_threads[threading.current_thread()] = username
    return True


def _logout():
    t = threading.current_thread()
    if t in _user_threads:
        del _user_threads[t]


def thread_owner():
    t = threading.current_thread()
    if t in _user_threads:
        return _user_threads[t]
    return 'system'


def thread_count():
    return len(_user_threads)


def require_permissions(role):
    t = threading.current_thread()
    if t not in _user_threads:
        raise UserPermissionsRequired()
    username = _user_threads[t]
    results = list(_user_db.query("SELECT users.username, users.role, roles.role, roles.weight FROM users, roles WHERE users.username == ? AND users.role == roles.role AND roles.weight <= 0", (username,)))
    if len(results) > 0:
        return True
    raise UserPermissionsRequired()


def hash_password(password):
    return hashlib.sha256(bytes(password, 'utf-8')).hexdigest()


