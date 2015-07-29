#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import shutil
import time
import traceback

import json


class ConfigInfo (object):
    def __init__(self):
        self.settings = [ ]

    def add_setting(self, name, propername, default=None, datatype=None):
        for i in range(len(self.settings)):
            if self.settings[i]['name'] == name:
                del self.settings[i]
                break

        # other valid datatypes are: textarea
        if not datatype:
            datatype = type(default).__name__

        self.settings.append({
            'name' : name,
            'propername' : propername,
            'default' : default,
            'datatype' : datatype,
            'options' : None
        })

    def add_option(self, settingname, propername, value):
        for setting in self.settings:
            if setting['name'] == settingname:
                if not setting['options']:
                    setting['options'] = [ ]
                setting['options'].append( (propername, value) )

    def get_defaults(self):
        defaults = { }
        for setting in self.settings:
            defaults[setting['name']] = setting['default']
        return defaults

    def get_proper_names(self):
        return [ (setting['name'], setting['propername'], setting['datatype']) for setting in self.settings ]


class ObjectNode (object):
    def __init__(self, **config):
        self._parent = None
        self._children = { }
        self.set_config_data(config)

    @staticmethod
    def get_config_info():
        return ConfigInfo()

    def set_config_data(self, config):
        self._config = config
        self._config['__type__'] = self.__class__.__module__.replace('nerve.', '').replace('.', '/') + "/" + self.__class__.__name__
        if '__children__' in config:
            self._children = self.make_object_table(config['__children__'])
            for objname in self._children.keys():
                self._children[objname].parent = self

    def get_config_data(self):
        self._config['__children__'] = self.save_object_table(self._children)
        return self._config

    def set_setting(self, name, value):
        try:
            self._config[name] = value
        except:
            print (traceback.format_exc())

    def get_setting(self, name, typename=None):
        if name in self._config:
            return self._config[name]
        return None


    def __getattr__(self, index):
        attrib = self.get_child(index)
        if attrib:
            return attrib
        #if '_config' in self.__dict__ and index in self.__dict__['_config']:
        #    return self.__dict__['_config'][index]
        raise AttributeError("'%s' object has no attribute '%s'" % (str(self), index))

    def keys(self):
        return self.keys_children() # + list(self._config.keys()) #+ [ name for name in dir(self) if name[0] != '_' ]


    def get_child(self, index):
        if index in self.__dict__['_children']:
            return self.__dict__['_children'][index]
        return None

    def set_child(self, index, obj):
        if isinstance(obj, ObjectNode):
            obj.parent = self
        self._children[index] = obj

    def del_child(self, index):
        if index in self._children:
            del self._children[index]
            return True
        return False

    def keys_children(self):
        return list(self._children.keys())


    def get_object(self, name):
        obj = self
        for segment in name.split('/'):
            obj = getattr(obj, segment)
        return obj

    def set_object(self, name, obj, **config):
        if type(obj) == str:
            obj = ObjectNode.make_object(obj, config)
        if not obj:
            nerve.log("error creating object " + name)
            return None

        root = self
        (*segments, leaf) = name.split('/')        
        for segment in segments:
            root = getattr(root, segment)
        #root[leaf] = obj
        root.set_child(leaf, obj)

    def del_object(self, name):
        root = self
        (*segments, leaf) = name.split('/')        
        for segment in segments:
            root = getattr(root, segment)
        return root.del_child(leaf)


    @staticmethod
    def make_object(typeinfo, config):
        classtype = ModulesDirectory.get_module(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        config_data = classtype.get_config_info().get_defaults()
        config_data.update(config)
        config_data['__type__'] = typeinfo
        obj = classtype(**config_data)
        return obj

    @staticmethod
    def get_class_config_info(typeinfo):
        classtype = ModulesDirectory.get_module(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        return classtype.get_config_info()

    @staticmethod
    def make_object_table(config):
        objects = { }
        for objname in config.keys():
            if objname != '__type__':
                if '__type__' not in config[objname]:
                    typeinfo = "objects/ObjectNode"
                else:
                    typeinfo = config[objname]['__type__']
                obj = ObjectNode.make_object(typeinfo, config[objname])
                objects[objname] = obj
        return objects

    @staticmethod
    def save_object_table(objects):
        config = { }
        for objname in objects.keys():
            config[objname] = objects[objname].get_config_data()
        return config


class SymbolicLink (ObjectNode):
    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('link', "Link", default="")
        return config_info

    def __getitem__(self, index):
        link = self.get_setting('link')
        return nerve.get_object(link + '/' + str(index))

    def __setitem__(self, index, obj):
        link = self.get_setting('link')
        nerve.set_object(link + '/' + str(index), obj)

    #def __delitem__(self, index):
    #    delattr(self.objects, index)


class Module (ObjectNode):
    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('name', "Module Name", default="")
        return config_info


class ModulesDirectory (ObjectNode):
    loaded_modules = { }

    """
    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('autoload', "Auto Load", default=[ 'base' ])
        return config_info
    """

    """
    def set_config_data(self, config):
        #super(ObjectNode, self).set_config_data(config)
        ObjectNode.set_config_data(self, config)
        #self.autoload_modules()
    """

    def get_config_data(self):
        return self._config

    """
    def __getattr__(self, name):
        res = getattr(nerve, name)
        return res
    """

    """
    def keys(self):
        return dir(nerve)
    """

    def get_child(self, index):
        if index in ModulesDirectory.loaded_modules:
            return ModulesDirectory.loaded_modules[index]
        return None

    def set_child(self, index, obj):
        pass

    def del_child(self, index):
        return False

    def keys_children(self):
        return list(ModulesDirectory.loaded_modules.keys())


    """
    def autoload_modules(self):
        modules = self.get_setting('autoload')
        if modules:
            print ("loading modules")
            for name in modules:
                ModulesDirectory.import_module(name.replace('/', '.'))

    @staticmethod
    def preload_modules(modules):
        print ("preloading modules")
        for name in modules:
            ModulesDirectory.import_module(name)
    """

    def get_types(self, classtype=None, module=None):
        typelist = [ ]
        if not module:
            module = nerve
            typelist = [ 'objects/ObjectNode', 'core/QueryObject', 'events/Event' ]

        modulename = module.__name__
        for typename in dir(module):
            attrib = getattr(module, typename)

            if isinstance(attrib, type) and issubclass(attrib, classtype):
                typelist.append(modulename.replace('.', '/') + '/' + typename)
            elif isinstance(attrib, type(nerve)) and attrib.__package__.startswith(modulename):
                typelist.extend(self.get_types(classtype, attrib))

        # TODO holy fuck bad hack
        return [ typename.replace('nerve/', '') for typename in typelist ]
        #return typelist

    def get_modules(self):
        autoload = self.get_setting('autoload')
        modules = [ ]
        for filename in os.listdir('nerve/'):
            if filename != '__pycache__' and os.path.isdir('nerve/' + filename):
                modules.append( (filename, filename in autoload) )
        return sorted(modules)

    @staticmethod
    def get_module(modulename):
        #return ObjectNode.get_object(nerve, modulename)
        #return nerve.get_object("/modules/" + modulename)
        (modulename, _, objname) = modulename.rpartition('/')
        modulename = modulename.replace('/', '.')
        if modulename not in ModulesDirectory.loaded_modules:
            ModulesDirectory.import_module(modulename)
        return getattr(ModulesDirectory.loaded_modules[modulename], objname)


    @staticmethod
    def import_module(modulename):
        modulename = modulename.replace('/', '.')
        if modulename not in ModulesDirectory.loaded_modules:
            try:
                module = eval("nerve." + modulename)
            except:
                module = None

            if module and type(module) == type(nerve):
                ModulesDirectory.loaded_modules[modulename] = module
            else:
                try:
                    nerve.log("loading module " + modulename)
                    code = 'import nerve.%s\n#nerve.%s.init()' % (modulename, modulename)
                    exec(code, globals(), globals())
                    ModulesDirectory.loaded_modules[modulename] = eval("nerve." + modulename)
                except ImportError as e:
                    """
                    # TODO this is a temporary hack...
                    #nerve.log("error loading module " + modulename + "\n\n" + traceback.format_exc())
                    nerve.log("loading module " + modulename)
                    code = 'import local.%s\n#%s.init()' % (modulename, modulename)
                    exec(code, globals(), globals())
                    ModulesDirectory.loaded_modules[modulename] = eval("local." + modulename)
                    """
                    nerve.log("error loading module " + modulename + "\n\n" + traceback.format_exc())
        return ModulesDirectory.loaded_modules[modulename]

