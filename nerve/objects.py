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
        self._parent = None
        self._children = { }
        self.set_config_data(config)

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
            obj = Module.make_object(typeinfo, config[objname])
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

    def get_setting(self, name, typename=None):
        if name in self._config:
            return self._config[name]
        return None

    ### Direct ObjectNode Children ###

    def get_child(self, index):
        nerve.users.require_access('r', self._config['owner'], self._config['group'], self._config['access'])
        if index in self._children:
            return self._children[index]
        return None

    def set_child(self, index, obj):
        nerve.users.require_access('w', self._config['owner'], self._config['group'], self._config['access'])
        if isinstance(obj, ObjectNode):
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

    def get_root(self):
        if not self._parent:
            return None
        root = self._parent
        while root._parent:
            root = root._parent
        return root

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
            obj = Module.make_object(obj, config)
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

    """
    def notify(self, querystring, *args, **kwargs):
        if not querystring.endswith('/*'):
            raise Exception("Invalid notify query: " + querystring)
        results = [ ]
        parent = self.get_object(querystring.strip('/*'))
        for objname in sorted(parent.keys_children()):
            obj = parent.get_child(objname)
            if callable(obj):
                results.append(obj(*args, **kwargs))
        return results
    """

    def query(self, querystring, *args, **kwargs):
        (name, slash, remain) = querystring.partition('/')

        if name != '*':
            obj = self.get_object(name)
            if slash:
                return obj.query(remain, *args, **kwargs)
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


class _ModuleSingleton (type):
    def __call__(cls, **config):
        if 'name' not in config:
            config['name'] = 'nerve'

        if not cls.root:
            if config['name'] == 'nerve':
                cls.root = super(_ModuleSingleton, cls).__call__(**config)
            else:
                cls.root = super(_ModuleSingleton, cls).__call__(name='nerve')

        modulepath = config['name'].split('.')
        module = parentmodule = cls.root
        for (i, name) in enumerate(modulepath[1:], start=1):
            module = parentmodule.get_child(name)
            if not module:
                if i + 1 == len(modulepath):
                    module = super(_ModuleSingleton, cls).__call__(**config)
                else:
                    module = super(_ModuleSingleton, cls).__call__(name='.'.join(modulepath[:i+1]))
                parentmodule.set_child(name, module)
            parentmodule = module

        #print("would have set data to " + repr(config))
        #module.set_config_data(config)
        return module


class Module (ObjectNode, metaclass=_ModuleSingleton):
    root = None

    def __init__(self, **config):
        self._module = self.get_module(config['name'])
        super().__init__(**config)
        self._name = self.get_setting('name')
        #self._module = eval(self._name)

    def get_config_info(self=None):
        config_info = ObjectNode.get_config_info()
        config_info.add_setting('name', "Full Name", default='nerve')

        if self and self._module:
            if hasattr(self._module, 'get_config_info'):
                config_info = self._module.get_config_info(config_info)
        return config_info

    """
    def get_child(self, index):
        child = super().get_child(index)
        #if not child:
        #    child = getattr(self._module, index)
        return child
    """

    #def set_child(self, index, obj):
    #    pass

    def del_child(self, index):
        return False

    def __getattr__(self, index):
        attrib = self.get_child(index)
        if attrib:
            return attrib

        attrib = getattr(self._module, index)
        if attrib:
            return attrib
        raise AttributeError("'%s' object has no attribute '%s'" % (str(self), index))

    # TODO is this used anywhere?
    def keys(self):
        keys = super().keys()
        print(keys)
        keys = keys + [ name for name in dir(self._module) if not name.startswith('_') and name not in keys ]
        print(keys)
        return keys

    # TODO this doesn't work because it only gets proper modules
    def get_module_list(self):
        return self.keys_children()

    @classmethod
    def get_types(cls, classtype=ObjectNode, module=nerve):
        typelist = set()
        modulename = module.__name__
        for attribname in dir(module):
            attrib = getattr(module, attribname)
            if isinstance(attrib, type) and issubclass(attrib, classtype) and attrib.__module__ == modulename:
                typelist.add(modulename.replace('nerve.', '').replace('.', '/') + '/' + attribname)
            elif isinstance(attrib, types.ModuleType) and attrib.__package__.startswith(modulename) and attrib.__name__ != 'nerve':
                typelist.update(cls.get_types(classtype, attrib))
        return sorted(typelist)

    @classmethod
    def get_class(cls, typeinfo):
        (modulename, _, classname) = typeinfo.rpartition('/')
        module = cls.get_module(modulename)
        return getattr(module, classname)

    @classmethod
    def get_module(cls, modulename):
        modulename = cls.get_python_name(modulename)

        modulepath = modulename.split('.')
        module = parentmodule = nerve
        for (i, name) in enumerate(modulepath[1:], start=1):
            try:
                module = getattr(parentmodule, name)
            except:
                module = None

            if not module:
                module = cls.import_module('.'.join(modulepath[:i+1]))
            parentmodule = module
        return module

    @classmethod
    def import_module(cls, modulename):
        """
        nerve.log("loading module " + modulename)
        try:
            exec("import " + modulename, globals(), globals())
        except ImportError:
            nerve.log("failed loading module " + modulename, logtype='error')
            modulename = modulename.replace("nerve.", "modules.")
            nerve.log("loading module " + modulename)
            exec("import " + modulename, globals(), globals())
        #    nerve.log("error loading module " + modulename + "\n\n" + traceback.format_exc(), logtype='error')
        #    return

        module = eval(modulename)

        if hasattr(module, 'init'):
            init = getattr(module, 'init')
            init()

        return module
        """

        modulename = modulename.replace("nerve.", "")
        nerve.log("loading module " + modulename)
        for namespace in ('nerve', 'modules'):
            currentname = '.'.join((namespace, modulename))
            try:
                exec("import " + currentname, globals(), globals())
                #module = importlib.import_module(currentname)
                #print(module)

            except ImportError as e:
                if e.name == currentname:
                    continue
                else:
                    nerve.log(traceback.format_exc(), logtype='error')
                    break

            except:
                nerve.log(traceback.format_exc(), logtype='error')
                break

            else:
                module = eval(currentname)
                if hasattr(module, 'init'):
                    init = getattr(module, 'init')
                    init()
                return module
        nerve.log("unable to load module " + modulename, logtype='error')
        return None

    @staticmethod
    def get_python_name(modulename):
        if modulename.startswith('/modules/'):
            modulename = modulename[len('/modules/'):]
        modulename = modulename.replace('/', '.')
        if modulename[0] == '.':
            raise Exception("attempting to import invalid module: " + modulename)
        if not modulename.startswith('nerve'):
            modulename = 'nerve.' + modulename
        return modulename

    @classmethod
    def make_object(cls, typeinfo, config):
        classtype = cls.get_class(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        obj = classtype(**config)
        return obj

    @classmethod
    def get_class_config_info(cls, typeinfo):
        classtype = cls.get_class(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        return classtype.get_config_info()


