#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve


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

        for typeinfo in reversed(typeinfo.split(':')):
            (name, args) = cls.parse_type(typeinfo)
            if name not in cls._datatypes:
                raise Exception("Unregistered subtype '" + name + "' in datatype " + typeinfo)
            if datatype:
                datatype = type(cls._datatypes[name])(datatype, *args)
            elif args:
                datatype = type(cls._datatypes[name])(*args)
            else:
                datatype = cls._datatypes[name]
        return datatype

    @classmethod
    def parse_type(cls, typeinfo):
        (name, _, args) = typeinfo.partition('(')
        if not args:
            return (name, ())
        args = args.strip()
        (last, args) = (args[-1], args[:-1])
        if last != ')' or '(' in args or ')' in args:
            raise Exception("parse error in type description " + repr(typeinfo))
        return (name, [ arg.strip() for arg in args.split(',') ])

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

    def render(self, data):
        return str(data)

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


@RegisterConfigType('hidden')
class HiddenConfigType (ScalarConfigType):
    htmltype = 'hidden'
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
    def __init__(self, superclass=None):
        super().__init__()
        self.options = [ ]
        self.superclass = superclass

    def validate(self, data):
        # TODO check to make sure the object of that name exsists
        return str(data)

    def get_options(self):
        self.options = [ ("(select object type)", '') ]
        superclass = nerve.Module.get_class(self.superclass) if self.superclass else None
        print(superclass)
        for typename in nerve.Module.get_types():
            if not superclass or issubclass(nerve.Module.get_class(typename), superclass):
                self.options.append( (typename, typename) )
        return self.options


@RegisterConfigType('object')
class ObjectConfigType (ComplexConfigType):
    def __init__(self, superclass=None):
        super().__init__()
        self.superclass = superclass

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
        elif isinstance(data, nerve.ObjectNode):
            typename = data.get_setting('__type__')
            items = data.get_config_info().get_items(data)
            children = [ (key, data.get_child(key)) for key in data.keys_children() ]
        elif type(data) == dict:
            typename = data['__type__']
            items = nerve.Module.get_class_config_info(typename).get_items(data)
            children = data['__children__'].items() if '__children__' in data else ()
        else:
            raise ValueError("Invalid datatype in get_items(): " + type(data).__name__)

        yield ('__type__', 'Type', ConfigType.get_type('object-type' + ('({0})'.format(self.superclass) if self.superclass else '')), typename)
        for tup in items:
            yield tup
        # TODO might the key here get mixed up with a setting of the same name?
        for (key, item) in sorted(children):
            yield (key, key, self, item)


class StructConfigType (ComplexConfigType):
    def __init__(self):
        super().__init__()
        self.settings = [ ]
        self.children = None

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

    def add_default_child(self, childname, config):
        if not self.children:
            self.children = { }
        self.children[childname] = config

    def set_default(self, name, default):
        for setting in self.settings:
            if setting['name'] == name:
                setting['default'] = default
                return

    def get_defaults(self):
        defaults = { }
        for setting in self.settings:
            defaults[setting['name']] = setting['default']
        if self.children:
            defaults['__children__'] = self.children.copy()
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


@RegisterConfigType('user-id')
class UserIDConfigType (IntConfigType):
    def __init__(self):
        super().__init__()
        self.options = [ ]

    def validate(self, data):
        # TODO check to make sure the object of that name exsists
        return int(data)

    def get_options(self):
        return [ (user['username'], user['uid']) for user in nerve.users.get_user_list() ]


@RegisterConfigType('group-id')
class GroupIDConfigType (IntConfigType):
    def __init__(self):
        super().__init__()
        self.options = [ ]

    def validate(self, data):
        # TODO check to make sure the object of that name exsists
        return int(data)

    def get_options(self):
        return [ (group['groupname'], group['gid']) for group in nerve.users.get_group_list() ]


@RegisterConfigType('access')
class AccessConfigType (IntConfigType):
    def __init__(self):
        super().__init__()
        self.options = [ ]

    def validate(self, data):
        access = int(data, 8)
        if access < 0 or access > 0o777:
            raise ValueError("Invalid access permissions: %o" % (access,))
        return access

    def render(self, data):
        if data is None:
            return '0o755'
        return oct(data)

