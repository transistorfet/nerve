#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import hashlib
import threading
import traceback


UID_ADMIN = 0
UID_SYSTEM = 1

GID_ADMIN = 0
GID_SYSTEM = 1

class UserLoginError (Exception): pass
class UserPermissionsError (Exception): pass
class UserPermissionsRequired (Exception): pass


_user_db = None
_user_threads = { }

def init():
    global _user_db
    _user_db = nerve.Database('users.sqlite')

    if not _user_db.table_exists('groups'):
        _user_db.create_table('groups', "gid INTEGER PRIMARY KEY, groupname TEXT, weight NUMERIC")
        add_group(GID_ADMIN, 'admin', 0)
        add_group(GID_SYSTEM, 'system', 1000)
        add_group(-1, 'user', 100)
        add_group(-1, 'guest', 500)

    if not _user_db.table_exists('users'):
        _user_db.create_table('users', "uid INTEGER PRIMARY KEY, username TEXT, password TEXT, groups TEXT, last_login NUMERIC")
        add_user(UID_ADMIN, 'admin', 'admin', 'admin')
        add_user(UID_SYSTEM, 'system', None, 'system')
        add_user(-1, 'guest', '', 'guest')

    _user_db.create_table('user_data', "uid INTEGER PRIMARY KEY, dataname TEXT, data TEXT")



def add_user(uid, username, password, *groups):
    _user_db.where('username', username)
    if uid >= 0:
        _user_db.or_where('uid', uid)
    results = list(_user_db.get('users'))
    if len(results) > 0:
        return False

    gids = [ ]
    for groupname in groups:
        _user_db.select('gid')
        _user_db.where('groupname', groupname)
        results = list(_user_db.get('groups'))
        if len(results) <= 0:
            return False
        gids.append(str(results[0][0]))

    userrec = { 'username' : username, 'password' : hash_password(password) if password != None else None, 'groups' : ','.join(sorted(gids)) }
    if uid >= 0:
        userrec['uid'] = uid
    _user_db.insert('users', userrec)
    return True


def add_group(gid, groupname, weight):
    _user_db.where('groupname', groupname)
    if gid >= 0:
        _user_db.or_where('gid', gid)
    results = list(_user_db.get('groups'))
    if len(results) > 0:
        return False

    grouprec = { 'groupname' : groupname, 'weight' : weight }
    if gid >= 0:
        grouprec['gid'] = gid
    _user_db.insert('groups', grouprec)
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
    _user_db.select('uid,username,groups')
    _user_db.where('username', username)
    _user_db.where('password', password)
    results = list(_user_db.get('users'))
    if len(results) <= 0:
        return False
    # set the thread record to this user: (uid, username, list of groupids)
    _user_threads[threading.current_thread()] = ( results[0][0], results[0][1], [ int(gid) for gid in results[0][2].split(',') ] )

    # update the last login field
    _user_db.where('uid', results[0][0])
    _user_db.update('users', { 'last_login' : time.time() })
    return True


def _logout():
    t = threading.current_thread()
    if t in _user_threads:
        del _user_threads[t]


def thread_owner():
    t = threading.current_thread()
    if t in _user_threads:
        return _user_threads[t][1]
    return 'system'


def thread_owner_id():
    t = threading.current_thread()
    if t in _user_threads:
        return _user_threads[t][0]
    return -1


def thread_owner_info():
    t = threading.current_thread()
    if t in _user_threads:
        return ( _user_threads[t][0], _user_threads[t][1], _user_threads[t][2].copy() )
    return (-1, 'system', [ ] )


def thread_count():
    return len(_user_threads)


def require_permissions(role):
    uid = thread_owner_id()
    if uid < 0:
        raise UserPermissionsRequired()
    results = list(_user_db.query("SELECT users.uid, users.groups, groups.gid, groups.weight FROM users, groups WHERE users.uid == ? AND ','+users.groups+',' LIKE '%,'+groups.gid+',%' AND groups.weight <= 0", (uid,)))
    if len(results) > 0:
        return True
    raise UserPermissionsRequired()


def require_access(require, owner, group, access):
    #print(traceback.print_stack())
    #print(thread_owner())
    require = 0o1 if require == 'r' else 0o2 if require == 'w' else 0o4 if require == 'w' else require
    (uid, username, gids) = thread_owner_info()
    if uid == owner or GID_ADMIN in gids:
        require <<= 6
    elif group in gids:
        require <<= 3
    if not (access & require):
        raise UserPermissionsError("owner: %d, group: %d, access: %o <-/-> thread owner: %d, groups: %s" % (owner, group, access, uid, repr(gids)))


def get_user_list():
    _user_db.select('username,uid')
    return list(_user_db.get('users'))


def get_group_list():
    _user_db.select('groupname,gid')
    return list(_user_db.get('groups'))


def hash_password(password):
    return hashlib.sha256(bytes(password, 'utf-8')).hexdigest()


