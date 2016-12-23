#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import types
import traceback
import importlib


def get_types(classtype, module=nerve):
    typelist = set()
    modulename = module.__name__
    for attribname in dir(module):
        attrib = getattr(module, attribname)
        if isinstance(attrib, type) and issubclass(attrib, classtype) and attrib.__module__ == modulename:
            typelist.add(modulename.replace('nerve.', '').replace('.', '/') + '/' + attribname)
        elif isinstance(attrib, types.ModuleType) and attrib.__package__.startswith(modulename) and attrib.__name__ != 'nerve':
            typelist.update(get_types(classtype, attrib))
    return sorted(typelist)


def get_class(typeinfo):
    (modulename, _, classname) = typeinfo.rpartition('/')
    module = get_module(modulename)
    return getattr(module, classname)


def get_module(modulename):
    modulename = get_python_name(modulename)

    modulepath = modulename.split('.')
    # TODO this causes problems when you import something from modules. instead of nerve.  It causes an infinite loop
    module = parentmodule = nerve
    for (i, name) in enumerate(modulepath[1:], start=1):
        try:
            module = getattr(parentmodule, name)
        except:
            module = None

        if not module:
            module = import_module('.'.join(modulepath[:i+1]))
        parentmodule = module
    return module


def get_python_name(modulename):
    if modulename.startswith('/modules/'):
        modulename = modulename[len('/modules/'):]
    modulename = modulename.replace('/', '.')
    if modulename[0] == '.':
        raise Exception("attempting to import invalid module: " + modulename)
    if not modulename.startswith('nerve'):
        modulename = 'nerve.' + modulename
    return modulename


def import_module(modulename):
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
            if hasattr(module, 'Module'):
                moduleclass = getattr(module, 'Module')
                moduleclass(__type__=modulename.replace('.', '/') + '/Module')
            return module
    nerve.log("unable to load module " + modulename, logtype='error')
    return None



class _MetaModule (type):
    def __call__(cls, **config):
        #(modulename, _, classname) = config['__type__'].rpartition('/')
        #modulename = get_python_name(modulename)
        modulename = cls.__module__

        if modulename in cls._modules:
            obj = cls._modules[modulename]
            obj.set_config_data(config)
            return obj
        else:
            obj = super().__call__(**config)
            cls._modules[modulename] = obj
            return obj


class Module (nerve.ObjectNode, metaclass=_MetaModule):
    _modules = { }

    def __init__(self, **config):
        #self._module = get_module(config['name'])
        #(modulename, _, classname) = config['__type__'].rpartition('/')
        #print('PREINIT', modulename, self.__module__)
        self._module = get_module(self.__module__ if self.__module__ != 'nerve.modules' else 'nerve')
        super().__init__(**config)
        #print('INIT', modulename, self.__module__)
        #self._module = eval(self._name)

    #def get_child(self, index):
    #    child = super().get_child(index)
    #    #if not child:
    #    #    child = getattr(self._module, index)
    #    return child

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


"""
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


class Module (nerve.ObjectNode, metaclass=_ModuleSingleton):
    root = None

    def __init__(self, **config):
        traceback.print_stack()
        self._module = get_module(config['name'])
        super().__init__(**config)
        self._name = self.get_setting('name')
        #self._module = eval(self._name)

    def get_config_info(self=None):
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('name', "Full Name", default='nerve')

        if self and self._module:
            if hasattr(self._module, 'get_config_info'):
                config_info = self._module.get_config_info(config_info)
        return config_info

    #def get_child(self, index):
    #    child = super().get_child(index)
    #    #if not child:
    #    #    child = getattr(self._module, index)
    #    return child

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
"""

