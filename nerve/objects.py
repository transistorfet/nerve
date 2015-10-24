#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import types
import traceback


class ConfigType (object):
    _datatypes = { }

    htmltype = 'text'

    @classmethod
    def get_type(cls, typeinfo, itemtype=None):
        if isinstance(itemtype, ConfigType):
            datatype = itemtype
        elif type(itemtype) == str:
            datatype = cls.get_type(itemtype)
        else:
            datatype = None

        for name in reversed(typeinfo.split(':')):
            if name not in cls._datatypes:
                raise Exception("Unregistered subtype '" + name + "' in datatype " + typeinfo)
            if not datatype:
                datatype = cls._datatypes[name]
            else:
                datatype = type(cls._datatypes[name])(datatype)
        return datatype

    @classmethod
    def register_type(cls, name, obj):
        cls._datatypes[name] = obj

    def is_type(self, typeinfo):
        datatype = self
        for name in typeinfo.split(':'):
            if name not in self._datatypes:
                return False
            if not issubclass(type(datatype), type(self._datatypes[name])):
                return False
            datatype = datatype.itemtype if hasattr(datatype, 'itemtype') else None
        return True

    def __init__(self):
        self.options = None

    def validate(self, data):
        raise NotImplementedError

    def get_items(self, data):
        return ()

    def get_options(self):
        return self.options


def RegisterConfigType(name):
    def CreateTypeFromClass(cls):
        ConfigType.register_type(name, cls())
        return cls
    return CreateTypeFromClass


@RegisterConfigType('scalar')
class ScalarConfigType (ConfigType):
    pass


@RegisterConfigType('complex')
class ComplexConfigType (ConfigType):
    htmltype = None


@RegisterConfigType('container')
class ContainerConfigType (ComplexConfigType):
    def __init__(self, itemtype=None):
        super().__init__()
        self.itemtype = itemtype


@RegisterConfigType('bool')
class BoolConfigType (ScalarConfigType):
    htmltype = 'checkbox'
    def validate(self, data):
        if type(data) == bool:
            return data

        val = str(data).lower()
        if val == 'true':
            return True
        elif val == 'false':
            return False
        else:
            raise ValueError("Invalid data for " + setting['name'] + ". Expected bool")


@RegisterConfigType('int')
class IntConfigType (ScalarConfigType):
    def validate(self, data):
        return int(data)


@RegisterConfigType('float')
class FloatConfigType (ScalarConfigType):
    def validate(self, data):
        return float(data)


@RegisterConfigType('str')
class StrConfigType (ScalarConfigType):
    def validate(self, data):
        return str(data)


@RegisterConfigType('textarea')
class TextAreaConfigType (ScalarConfigType):
    htmltype = 'textarea'
    def validate(self, data):
        return str(data)


@RegisterConfigType('bytes')
class BytesConfigType (ScalarConfigType):
    def validate(self, data):
        return bytes(data, 'utf-8')


@RegisterConfigType('filename')
class FilenameConfigType (ScalarConfigType):
    def validate(self, data):
        if type(data) != str:
            raise ValueError("expected type 'str', received type '" + type(data).__name__ + "'")
        segments = data.split('/')
        if '.' in segements or '..' in segements:
            raise ValueError("filenames cannot contain '.' or '..'")
        # TODO check if the file exists?  for a normal file that's needed, but for js/css files, they are relative to the webserver path, so os.path.exists would fail
        #       what if... you specify the actual file and the template or something converts those names to externally reachable addresses... might be too complicated to
        #       get the server/controllers, and it might be a bit confusing, but it would make it easier to have controllers not at the root of the path (eg. /something/medialib
        #       which would need to refer to /something/medialib/assets/js/medialib.js)
        return data


@RegisterConfigType('list')
class ListConfigType (ContainerConfigType):
    def validate(self, data):
        if type(data) != list:
            raise ValueError("expected type 'list', received type '" + type(data).__name__ + "'")
        result = [ ]
        for item in data:
            result.append(self.itemtype.validate(item))
        return result

    def get_items(self, data):
        for (key, value) in enumerate(data):
            yield (str(key), str(key), self.itemtype, value)


@RegisterConfigType('dict')
class DictConfigType (ContainerConfigType):
    def validate(self, data):
        if type(data) != dict:
            raise ValueError("expected type 'dict', received type '" + type(data).__name__ + "'")
        result = { }
        for (key, item) in data.items():
            result[key] = self.itemtype.validate(item)
        return result

    def get_items(self, data):
        if not data:
            return ()
        for (key, value) in sorted(data.items()):
            yield (key, key, self.itemtype, value)


@RegisterConfigType('object-type')
class ObjectTypeConfigType (StrConfigType):
    def __init__(self):
        super().__init__()
        self.options = [ ]

    def validate(self, data):
        # TODO check to make sure the object of that name exsists
        return str(data)

    def get_options(self):
        self.options = [ ("(select object type)", '') ]
        for typename in nerve.Module.get_types():
            self.options.append( (typename, typename) )
        return self.options


@RegisterConfigType('object')
class ObjectConfigType (ComplexConfigType):
    def validate(self, data):
        if type(data) != dict:
            raise ValueError("expected type 'dict', received type '" + type(data).__name__ + "'")
        if '__type__' not in data:
            raise ValueError("object config must contain the __type__ key")

        typeinfo = data['__type__']
        configinfo = nerve.Module.get_class(typeinfo).get_config_info()
        config = configinfo.validate(data)
        config['__type__'] = typeinfo
        return config

    def get_items(self, data):
        #return sorted(data.items())
        # TODO you should add the __type__ here, specifically, as a setting with options set to any object that can be used...
        # you'd have to add some javascript that would somehow update the items...
        if not data:
            typename = ''
            items = ()
            children = ()
        elif isinstance(data, ObjectNode):
            typename = data.get_setting('__type__')
            items = data.get_config_info().get_items(data)
            children = [ (key, data.get_child(key)) for key in data.keys_children() ]
        elif type(data) == dict:
            typename = data['__type__']
            items = Module.get_class_config_info(typename).get_items(data)
            children = data['__children__'].items() if '__children__' in data else ()
        else:
            raise ValueError("Invalid datatype in get_items(): " + type(data).__name__)

        yield ('__type__', 'Type', ConfigType.get_type('object-type'), typename)
        for tup in items:
            yield tup
        # TODO might the key here get mixed up with a setting of the same name?
        for (key, item) in sorted(children):
            yield (key, key, self, item)


class StructConfigType (ComplexConfigType):
    def __init__(self):
        super().__init__()
        self.settings = [ ]

    def add_setting(self, name, propername, default=None, datatype=None, itemtype=None, weight=0):
        for i in range(len(self.settings)):
            if self.settings[i]['name'] == name:
                del self.settings[i]
                break

        # attempt to guess the datatype if it's not given
        if not datatype:
            datatype = type(default).__name__

        datatype_class = ConfigType.get_type(datatype, itemtype)
        if not datatype_class:
            raise Exception("Unsupported setting datatype: " + datatype)

        setting = {
            'name' : name,
            'propername' : propername,
            'default' : default,
            'datatype' : datatype_class,
            'options' : None,
            'weight' : weight
        }

        i = 0
        while i < len(self.settings) and self.settings[i]['weight'] <= weight:
            i += 1
        self.settings.insert(i, setting)

    def add_option(self, settingname, propername, value):
        for setting in self.settings:
            if setting['name'] == settingname:
                if not setting['options']:
                    setting['options'] = [ ]
                setting['options'].append( (propername, value) )

    def set_default(self, name, default):
        for setting in self.settings:
            if setting['name'] == name:
                setting['default'] = default
                return

    def get_defaults(self):
        defaults = { }
        for setting in self.settings:
            defaults[setting['name']] = setting['default']
        return defaults

    def validate(self, data, itemtype=None):
        config = { }
        for setting in self.settings:
            if setting['name'] not in data:
                #config[setting['name']] = setting['default']
                pass
            else:
                config[setting['name']] = setting['datatype'].validate(data[setting['name']])
        return config

    def get_items(self, data):
        if not data:
            data = { }
        for setting in self.settings:
            value = data[setting['name']] if setting['name'] in data else setting['default']
            yield (setting['name'], setting['propername'], setting['datatype'], value)

    def __len__(self):
        return len(self.settings)



def public(funcobj):
    """ make function publically accessible through queries """
    funcobj.__ispublic__ = True
    return funcobj


def is_public(funcobj):
    if not hasattr(funcobj, '__ispublic__') or funcobj.__ispublic__ is not True:
        return False
    return True


class ObjectNode (object):
    def __init__(self, **config):
        self._parent = None
        self._children = { }
        self.set_config_data(config)

    ### Settings ###

    @classmethod
    def get_config_info(cls):
        config_info = StructConfigType()
        # TODO should these be number/ids? or the username/groupname
        #config_info.add_setting('owner', "Owner", default=nerve.users.thread_owner())
        #config_info.add_setting('group', "Group\Role", default='system')
        #config_info.add_setting('access', "Access", default='crw')     # full access: crwx

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
        if type(obj) == str:
            obj = Module.make_object(obj, config)
        if not obj:
            nerve.log("error creating object " + name, logtype='error')
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

    def notify(self, querystring, *args, **kwargs):
        if not querystring.endswith('/*'):
            raise Exception("Invalid notify query: " + querystring)
        parent = self.get_object(querystring.strip('/*'))
        for objname in parent.keys_children():
            obj = parent.get_child(objname)
            if callable(obj):
                obj(*args, **kwargs)


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
            except ImportError:
                nerve.log(traceback.format_exc(), logtype='error')
                continue
            else:
                module = eval(currentname)

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


