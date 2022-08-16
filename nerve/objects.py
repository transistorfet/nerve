#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import types
import traceback
import importlib


def public(funcobj):
    """ make function publically accessible through queries """
    funcobj.__ispublic__ = True
    return funcobj


def is_public(funcobj):
    if not hasattr(funcobj, '__ispublic__') or funcobj.__ispublic__ is not True:
        return False
    return True


def access(access):
    def access_wrapper(funcobj):
        def access_caller(*args, **kwargs):
            nerve.users.check_access(access)
            funcobj(*args, **kwargs)
        return access_caller
    return access_wrapper


def join_path(base, path):
    if not base or path[0] == '/' or '://' in path:
        return path
    return base.rstrip('/') + '/' + path


class ObjectNode (object):
    def __init__(self, **config):
        self._name = ''
        self._parent = None
        self._children = { }
        self.set_config_data(config)

    @staticmethod
    def make_object(typeinfo, config):
        classtype = nerve.modules.get_class(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        obj = classtype(**config)
        return obj

    @staticmethod
    def get_class_config_info(typeinfo):
        classtype = nerve.modules.get_class(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        return classtype.get_config_info()

    ### Settings ###

    @classmethod
    def get_config_info(cls):
        config_info = nerve.types.StructConfigType()
        config_info.add_setting('owner', "Owner", datatype='user-id', default=nerve.users.thread_owner_id())
        config_info.add_setting('group', "Group", datatype='group-id', default=-1)
        config_info.add_setting('access', "Access", datatype='access', default=0o755)

        #config_info.add_setting('__children__', "Child Objects", default=dict(), itemtype="object")
        # TODO if you had a means of dealing with objects as single settings, then you can use the dict recursive validator to add/remove/rename items
        return config_info

    def set_config_data(self, config):
        self._config = self.get_config_info().get_defaults()
        self.update_config_data(config)

        if '__children__' in config:
            if len(self._children):
                raise Exception("object already has children: " + self._config['__type__'] + " " + repr(self._children))
            self.make_object_children(config['__children__'])

    def update_config_data(self, config):
        # TODO should this maybe be only in the controller?
        #self.get_config_info().validate(config)
        self._config.update(config)
        self._config['__type__'] = self.__class__.__module__.replace('nerve.', '').replace('.', '/') + "/" + self.__class__.__name__

    def get_config_data(self):
        self._config['__children__'] = self.save_object_children()
        return self._config

    def make_object_children(self, config):
        for objname in config.keys():
            typeinfo = config[objname]['__type__'] if '__type__' in config[objname] else 'objects/ObjectNode'
            obj = self.make_object(typeinfo, config[objname])
            obj._name = objname
            obj._parent = self
            self._children[objname] = obj

    def save_object_children(self):
        config = { }
        for objname in self._children.keys():
            if isinstance(self._children[objname], ObjectNode):
                config[objname] = self._children[objname].get_config_data()
            else:
                nerve.log("unable to save child object " + objname + ": " + self._children[objname], logtype='error')
        return config

    def set_setting(self, name, value):
        try:
            self._config[name] = value
        except:
            nerve.log(traceback.format_exc(), logtype='error')

    def get_setting(self, name, default=None):
        if name in self._config:
            return self._config[name]
        return default

    ### Direct ObjectNode Children ###

    def get_child(self, index):
        nerve.users.require_access('r', self._config['owner'], self._config['group'], self._config['access'])
        if index in self._children:
            return self._children[index]
        return None

    def set_child(self, index, obj):
        nerve.users.require_access('w', self._config['owner'], self._config['group'], self._config['access'])
        if isinstance(obj, ObjectNode):
            obj._name = index
            obj._parent = self
        self._children[index] = obj

    def del_child(self, index):
        nerve.users.require_access('w', self._config['owner'], self._config['group'], self._config['access'])
        if index in self._children:
            del self._children[index]
            return True
        return False

    def keys_children(self):
        return list(self._children.keys())

    def parent(self):
        return self._parent

    def get_root(self):
        if not self._parent:
            return None
        root = self._parent
        while root._parent:
            root = root._parent
        return root

    def get_pathname(self, absolute=False):
        path = self._name
        obj = self._parent
        while obj:
            path = obj._name + '/' + path
            obj = obj._parent
        if absolute:
            return path
        else:
            return path.lstrip('/')

    ### Direct Attributes ###

    def __getattr__(self, index):
        attrib = self.get_child(index)
        if attrib:
            return attrib
        #if '_config' in self.__dict__ and index in self.__dict__['_config']:
        #    return self.__dict__['_config'][index]
        raise AttributeError("'%s' object has no attribute '%s'" % (str(self), index))

    def keys_attrs(self):
        return [ attrib for attrib in dir(self) if not attrib.startswith('_') ]

    def keys_queries(self):
        keys = [ ]
        for name in dir(self):
            obj = getattr(self, name)
            try:
                if obj.__ispublic__ is True:
                    keys.append(name)
            except:
                pass
        return keys

    ### Indirect Sub-Object Attributes ###

    def get_object(self, name):
        obj = self
        for segment in name.split('/'):
            obj = getattr(obj, segment)
        return obj

    def set_object(self, name, obj, **config):
        (path, _, leaf) = name.rpartition('/')
        root = self.get_object(path) if path else self

        if not root or not leaf:
            nerve.log("set_object(): invalid path given, " + name, logtype='error')
            return None

        if type(obj) == str:
            obj = self.make_object(obj, config)
        if not obj:
            nerve.log("error creating object " + name, logtype='error')
            return None

        root.set_child(leaf, obj)

    def del_object(self, name):
        (path, _, leaf) = name.rpartition('/')
        root = self.get_object(path)
        if not root or not leaf:
            nerve.log("del_object(): invalid path given, " + name, logtype='error')
            return None
        return root.del_child(leaf)

    def query(self, querystring, *args, **kwargs):
        (name, slash, remain) = querystring.partition('/')

        if name != '*':
            obj = self.get_object(name)
            if slash:
                if hasattr(obj, 'query'):
                    return obj.query(remain, *args, **kwargs)
                else:
                    raise NotImplementedError("can't resolve child of non-ObjectNode object")
            elif callable(obj):
                return obj(*args, **kwargs)
            else:
                return obj
        else:
            results = [ ]
            for key in self.keys_queries() + self.keys_children():
                path = key + ( '/' + remain if remain else '' )
                results.append(self.query(path, *args, **kwargs))
            return results

    def subscribe(self, topic, action, label=None, **eventmask):
        # TODO you could have this, and local resolution will do this, which ends in nerve.events.subscribe(self.get_pathname())
        pass


