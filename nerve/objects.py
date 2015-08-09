#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import traceback


class ConfigInfo (object):
    datatypes = { }

    @classmethod
    def register_type(cls, name, validator):
        cls.datatypes[name] = validator

    @classmethod
    def get_type(cls, name):
        return cls.datatypes[name]

    def __init__(self):
        self.settings = [ ]

    def add_setting(self, name, propername, default=None, datatype=None, iteminfo=None):
        for i in range(len(self.settings)):
            if self.settings[i]['name'] == name:
                del self.settings[i]
                break

        # attempt to guess the datatype if it's not given
        if not datatype:
            datatype = type(default).__name__

        if datatype not in self.datatypes:
            raise Exception("Unsupported setting datatype: " + datatype)

        self.settings.append({
            'name' : name,
            'propername' : propername,
            'default' : default,
            'datatype' : datatype,
            'iteminfo' : iteminfo,
            'options' : None
        })

    def add_option(self, settingname, propername, value):
        for setting in self.settings:
            if setting['name'] == settingname:
                if not setting['options']:
                    setting['options'] = [ ]
                setting['options'].append( (propername, value) )

    def __iter__(self):
        return iter(self.settings)

    def __len__(self):
        return len(self.settings)

    def get_defaults(self):
        defaults = { }
        for setting in self.settings:
            defaults[setting['name']] = setting['default']
        return defaults

    def validate_settings(self, args, defaults=False):
        config = { }
        for setting in self.settings:
            if setting['name'] not in args:
                if defaults:
                    config[setting['name']] = setting['default']
            elif setting['datatype'] in self.datatypes:
                validator = self.datatypes[setting['datatype']]
                config[setting['name']] = validator(args[setting['name']], setting['iteminfo'])
        return config


        # bool, int, float, str, textarea, bytes, tuple, list, dict... maybe also complex
        # datatype = list, subtype = 'bool|int|float|str|textarea'
        # actually it should be a subconfig info right?
        # subinfo = ConfigInfo()
        # subinfo.add_setting(None, 'Block Name', default='')



class ConfigTypeValidator (object):
    def __init__(self, func, htmltype="text", typeclass="scalar"):
        self.func = func
        self.htmltype = htmltype
        self.typeclass = typeclass

    def __call__(self, data, iteminfo=None):
        if iteminfo:
            return self.func(data, iteminfo)
        return self.func(data)

def ConfigTypeDecorator(htmltype="text", typeclass="scalar"):
    def CreateValidator(func):
        return ConfigTypeValidator(func, htmltype, typeclass)
    return CreateValidator

@ConfigTypeValidator
def BoolValidator(data):
    if type(data) == bool:
        config[setting['name']] = data
        return

    val = str(data).lower()
    if val == 'true':
        config[setting['name']] = True
    elif val == 'false':
        config[setting['name']] = False
    else:
        raise ValueError("Invalid data for " + setting['name'] + ". Expected bool")

ConfigInfo.register_type('bool', BoolValidator)
ConfigInfo.register_type('int', ConfigTypeValidator(int))
ConfigInfo.register_type('float', ConfigTypeValidator(float))
ConfigInfo.register_type('str', ConfigTypeValidator(str))
ConfigInfo.register_type('bytes', ConfigTypeValidator(bytes))
ConfigInfo.register_type('textarea', ConfigTypeValidator(str))
# also list, tuple, dict, object?
ConfigInfo.register_type('dict', ConfigTypeValidator(dict, htmltype=None))

@ConfigTypeDecorator(htmltype=None, typeclass="list")
def ListValidator(data):
    thing

ConfigInfo.register_type('list', ListValidator)

#Scalar:
# - display html element
# - package values from html element for post request
# - verify data conforms to type

#List:
# - add item (display complete html form for an item) (button displays form)
# for each item in the list
#  - display form for item, possibly collapsed (recursive)
#  - delete item that's displayed
#  - move item up or down
# - verify data, either force items to be accessed individually, or possibly allow entire list to be verified at once (how do you reference a subitem inside a config option)

#Dict:
# - add item (display complete html form for an item) (button displays form)
# for each item in dict
#  - display form for item, possibly collapsed (recursive)
#  - delete item that's displayed
#  - rename item that's displayed

#Object:
# - display complete form for all object settings (but you can't add or remove settings)
# - package values from html element for post request recursively
# - verify data conforms to type, again recursively



def querymethod(funcobj):
    """ function decorator to include method in the keys_queries() list """
    funcobj.__isquerymethod__ = True
    return funcobj


class ObjectNode (object):
    def __init__(self, **config):
        self._parent = None
        self._children = { }
        self.set_config_data(config)

    """ Settings """

    @classmethod
    def get_config_info(cls):
        config_info = ConfigInfo()
        #config_info.add_setting('__children__', "Child Objects", default=dict(), datatype="dict:object")
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
        #self.get_config_info().validate_settings(config)
        self._config.update(config)
        self._config['__type__'] = self.__class__.__module__.replace('nerve.', '').replace('.', '/') + "/" + self.__class__.__name__

    def get_config_data(self):
        self._config['__children__'] = self.save_object_children()
        return self._config

    def make_object_children(self, config):
        for objname in config.keys():
            typeinfo = config[objname]['__type__'] if '__type__' in config[objname] else 'objects/ObjectNode'
            obj = ObjectNode.make_object(typeinfo, config[objname])
            obj._parent = self
            self._children[objname] = obj

    def save_object_children(self):
        config = { }
        for objname in self._children.keys():
            config[objname] = self._children[objname].get_config_data()
        return config

    def set_setting(self, name, value):
        try:
            self._config[name] = value
        except:
            nerve.log(traceback.format_exc())

    def get_setting(self, name, typename=None):
        if name in self._config:
            return self._config[name]
        return None

    """ Direct ObjectNode Children """

    def get_child(self, index):
        if index in self._children:
            return self._children[index]
        return None

    def set_child(self, index, obj):
        if isinstance(obj, ObjectNode):
            obj._parent = self
        self._children[index] = obj

    def del_child(self, index):
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

    """ Direct Attributes """

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
                if obj.__isquerymethod__ is True:
                    keys.append(name)
            except:
                pass
        return keys

    """ Indirect Sub-Object Attributes """

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
        classtype = Module.get_class(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        obj = classtype(**config)
        return obj

    @staticmethod
    def get_class_config_info(typeinfo):
        classtype = Module.get_class(typeinfo)
        if not issubclass(classtype, ObjectNode):
            raise TypeError(str(typeinfo) + " is not a subclass of ObjectNode")
        return classtype.get_config_info()



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
        super().__init__(**config)
        self._name = self.get_setting('name')
        #self._module = eval(self._name)
        self._module = self.get_module(self._name)

        if hasattr(self._module, 'get_config_info'):
            defaults = self._module.get_config_info().get_defaults()
            defaults.update(self._config)
            self._config = defaults

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('name', "Full Name", default='nerve')
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
    """

    def get_types(self, classtype=None, module=None):
        return [ 'core/Server' ]

    # TODO this doesn't work because it only gets proper modules
    def get_module_list(self):
        return self.keys_children()

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
            nerve.log("failed loading module " + modulename)
            modulename = modulename.replace("nerve.", "modules.")
            nerve.log("loading module " + modulename)
            exec("import " + modulename, globals(), globals())
        #    nerve.log("error loading module " + modulename + "\n\n" + traceback.format_exc())
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
            try:
                exec("import " + '.'.join((namespace, modulename)), globals(), globals())
            except ImportError:
                continue

            else:
                module = eval('.'.join((namespace, modulename)))

                if hasattr(module, 'init'):
                    init = getattr(module, 'init')
                    init()
                return module
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


