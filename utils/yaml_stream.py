from yaml import Loader, load, safe_load

import re

try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader

def construct_yaml_str(self, node):
    # Override the default string handling function
    # to always return unicode objects
    return self.construct_scalar(node)

Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)

def read_by_list(file):
    y = file.readline()
    cont = 1
    while cont:
        l = file.readline()
        if len(l) == 0:
            cont = 0
            yield load(y, Loader=SafeLoader)
        else:
            if not l.startswith('-'):
                y = y + l
            else:
                yield load(y, Loader=SafeLoader)
                y = l

def read_by_any(file):
    y = file.readline()
    cont = 1
    while cont:
        l = file.readline()
        if len(l) == 0:
            cont = 0
            yield load(y, Loader=SafeLoader)
        else:
            # one of the eve yaml files has a line starting with an single quote
            if not re.match('^[^\s\']', l):
                y = y + l
            else:
                yield load(y, Loader=SafeLoader)
                y = l

def read_all(file):
    return load(file,Loader=SafeLoader)
