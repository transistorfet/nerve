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

        if not datatype:
            if type(default) in (float, int):
                datatype = 'number'
            elif type(default) is bool:
                datatype = 'bool'
            elif type(default) in (list, tuple):
                datatype = 'list'
            elif type(default) is dict:
                datatype = 'dict'
            else:
                datatype = 'string'

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
        return [ [ setting['name'], setting['propername'], setting['datatype'] ] for setting in self.settings ]


class ObjectNode (object):
    def __init__(self, **config):
        self.set_config_data(config)

    @staticmethod
    def get_config_info():
        return ConfigInfo()

    def set_config_data(self, config):
        self.config = config

    def get_config_data(self):
        return self.config

    def set_setting(self, name, value):
        try:
            self.config[name] = value
        except:
            print (traceback.format_exc())

    def get_setting(self, name, typename=None):
        if name in self.config:
            return self.config[name]
        return None

    # TODO maybe you should get rid of this? *shrug*
    def __getattr__(self, name):
        try:
            return self.__dict__['config'][name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (str(self), name))

    def __getitem__(self, index):
        return getattr(self, index)

    def __setitem__(self, index, obj):
        setattr(self, index, obj)

    def __delitem__(self, index):
        delattr(self, index)

    def keys(self):
        return [ name for name in dir(self) if name[0] != '_' ] + list(self.config.keys())

    def query_keys(self):
        return [ name for name in list(self.__class__.__dict__.keys()) + list(self.config.keys()) if name[0] != '_' ]

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
        #setattr(root, leaf, obj)
        root[leaf] = obj

    def load_config(self, filename):
        config = self.get_config_info().get_defaults()

        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                    nerve.log("config loaded from " + filename)
            except:
                nerve.log("error loading config from " + filename + "\n\n" + traceback.format_exc())
                return False
        modules = ModulesDirectory(**config['modules'])
        self.set_config_data(config)
        return True

    def save_config(self, filename):
        config = self.get_config_data()
        with open(filename, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def make_object(typeinfo, config):
        classtype = ModulesDirectory.get_module(typeinfo)
        #if not issubclass(classtype, ObjectNode):
        #    raise TypeError("")
        config_data = classtype.get_config_info().get_defaults()
        config_data.update(config)
        obj = classtype(**config_data)
        return obj

    @staticmethod
    def get_class_config_info(typeinfo):
        classtype = Modules.get_module(typeinfo)
        #if not isinstance(classtype, ObjectNode):
        #    raise TypeError("POOP")
        return classtype.get_config_info()


class ObjectDirectory (ObjectNode):
    def __init__(self, **config):
        self.objects = { }
        ObjectNode.__init__(self, **config)

    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        return config_info

    def set_config_data(self, config):
        self.objects = self.make_object_table(config)

    def get_config_data(self):
        config = self.save_object_table(self.objects)
        return config

    def __getattr__(self, name):
        if name in self.objects:
            return self.objects[name]

    def __getitem__(self, index):
        return self.objects[index]

    def __setitem__(self, index, obj):
        self.objects[index] = obj

    def __delitem__(self, index):
        delattr(self.objects, index)

    def keys(self):
        return self.objects.keys()

    @staticmethod
    def make_object_table(config):
        objects = { }
        for objname in config.keys():
            if objname != '__type__':
                if '__type__' not in config[objname]:
                    typeinfo = "objects/ObjectDirectory"
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


class Module (ObjectNode):
    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('name', "Module Name", default="")
        return config_info


class ModulesDirectory (ObjectDirectory):
    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectDirectory.get_config_info()
        config_info.add_setting('autoload', "Auto Load", default=[ 'base' ])
        return config_info

    def set_config_data(self, config):
        super(ObjectDirectory, self).set_config_data(config)
        self.autoload_modules()

    def get_config_data(self):
        return super(ObjectDirectory, self).config

    """
    def __getattr__(self, name):
        res = getattr(nerve, name)
        return res

    def __getitem__(self, index):
        return getattr(nerve, index)

    def __setitem__(self, index, obj):
        pass

    def __delitem__(self, index):
        pass

    def keys(self):
        return dir(nerve)
    """

    def autoload_modules(self):
        modules = self.get_setting('autoload')
        if modules:
            print ("loading modules")
            for name in modules:
                ModulesDirectory.import_module(name)

    def get_types(self, classtype=None):
        types = [ 'objects/ObjectDirectory' ]
        modules = self.get_setting('autoload')
        if modules:
            for name in modules:
                module = ObjectNode.get_object(nerve, name)
                for typename in dir(module):
                    attrib = getattr(module, typename)
                    if isinstance(attrib, type) and issubclass(attrib, classtype):
                        types.append(name.replace('.', '/') + '/' + typename)
        return types

    def get_modules(self):
        autoload = self.get_setting('autoload')
        modules = [ ]
        for filename in os.listdir('nerve/'):
            if filename != '__pycache__' and os.path.isdir('nerve/' + filename):
                modules.append( (filename, filename in autoload) )
        return sorted(modules)

    @staticmethod
    def get_module(modulename):
        return ObjectNode.get_object(nerve, modulename)
        #return nerve.get_object("/modules/" + modulename)

    @staticmethod
    def import_module(modulename):
        #self.set_object(modulename.replace('.', '/'), Module(name=modulename))
        try:
            nerve.log("loading module " + modulename)
            code = 'import nerve.%s\n#nerve.%s.init()' % (modulename, modulename)
            exec(code, globals(), globals())
            return eval("nerve." + modulename)
            #return globals()[modulename]
        except ImportError as e:
            # TODO this is a temporary hack...
            #nerve.log("error loading module " + modulename + "\n\n" + traceback.format_exc())
            nerve.log("loading module " + modulename)
            code = 'import local.%s\n#%s.init()' % (modulename, modulename)
            exec(code, globals(), globals())
            return eval("local." + modulename)
            #raise e


