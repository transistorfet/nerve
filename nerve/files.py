#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import os.path
import traceback


nerve_source_path = [ os.path.dirname(os.path.dirname(nerve.__file__)) ]
nerve_config_path = [ ]


def add_source_path(path):
    global nerve_source_path
    fullpath = os.path.abspath(path)
    if fullpath not in nerve_source_path:
        nerve_source_path.insert(0, fullpath)

def find_source(filename):
    for dirname in nerve_source_path:
        fullpath = os.path.join(dirname, filename)
        if os.path.exists(fullpath):
            return fullpath
    raise OSError("No source file found: \'{0}\'".format(filename))


def add_config_path(path):
    global nerve_config_path
    fullpath = os.path.abspath(path)
    if fullpath not in nerve_config_path:
        nerve_config_path.insert(0, fullpath)
        if not os.path.exists(fullpath):
            os.makedirs(fullpath)
        sys.path.insert(0, fullpath)
        add_source_path(fullpath)

def path(filename, create=False):
    if len(nerve_config_path) <= 0:
        raise OSError("No config directory set.")
    fullpath = os.path.join(nerve_config_path[0], filename)
    dirpath = os.path.dirname(fullpath)
    if create is True and not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return fullpath

def name(filename):
    if len(nerve_config_path) <= 0:
        raise OSError("No config directory set.")
    return os.path.join(nerve_config_path[0], filename)

def createfile(filename):
    fullpath = path(filename, create=True)
    if not os.path.exists(fullpath):
        open(fullpath, 'a').close()
    return fullpath

def createdir(dirname):
    if len(nerve_config_path) <= 0:
        raise OSError("No config directory set.")
    fullpath = os.path.join(nerve_config_path[0], dirname)
    if not os.path.exists(fullpath):
        os.makedirs(fullpath)
    return fullpath

def find(filename, create=False):
    for dirname in nerve_config_path:
        fullpath = os.path.join(dirname, filename)
        if os.path.exists(fullpath):
            return fullpath
    if create is True:
        return path(filename, create=True)
    raise OSError("No config file found: \'{0}\'".format(filename))

def load(filename):
    filename = find(filename)
    with open(filename, 'r') as f:
        contents = f.read()
    return contents

def save(filename, contents):
    filename = find(filename, create=True)
    with open(filename, 'w') as f:
        f.write(contents)

def validate(filename):
    for name in filename.rstrip('/'):
        if name == '' or name == '..':
            return False
    return True

