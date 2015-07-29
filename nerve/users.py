#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import hashlib


class Users (object):
    def __init__(self):
        self.db = nerve.Database('users.sqlite')
        self.db.create_table('users', "id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, last_login NUMERIC")
        self.db.create_table('user_data', "username TEXT PRIMARY KEY, dataname TEXT, data TEXT")
        if self.create_user('admin', 'admin', 'admin'):
            nerve.log("Created default user admin")

    def create_user(self, username, password, role):
        self.db.where('username', username)
        results = list(self.db.get('users'))
        if len(results) > 0:
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
        return True

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(bytes(password, 'utf-8')).hexdigest()

