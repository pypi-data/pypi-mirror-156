import os
import json
import yaml
from box import Box
from typing import IO, Any

class UndefinedEnvironmentVariable(Exception):
    pass

def isfloat(x: str):
    try:
        a = float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True

def isint(x: str):
    try:
        a = float(x)
        b = int(a)
    except (TypeError, ValueError):
        return False
    else:
        return a == b

def isjson(x: str) -> bool:
    try:
        json.loads(x)
        return True
    except ValueError as e:
        return False

class Loader(yaml.SafeLoader):
    """ A Customized YAML Loader for CFG1 """
    def __init__(self, stream: IO) -> None:
        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)

def _env(loader: Loader, node: yaml.Node) -> Any:
    """set value of key at node from environment variable"""
    if node.value in os.environ:
        val = os.environ.get(node.value)
        if isint(val):
            return int(val)
        if isfloat(val):
            return float(val)
        if isjson(val):
            return json.loads(val)
        return val
    raise UndefinedEnvironmentVariable('The environment variable %s is not defined' % (node.value))

def _env_def(loader: Loader, node: yaml.Node) -> Any:
    """set value of key at node from environment variable, or use the supplied default value """
    segs = node.value.split(',')
    key = segs[0].strip()
    val = segs[1].strip()
    if key in os.environ:
        val = os.environ.get(key)
    if isint(val):
        return int(val)
    if isfloat(val):
        return float(val)
    if isjson(val):
        return json.loads(val)
    return val

yaml.add_constructor('!env', _env, Loader)
yaml.add_constructor('!envdef', _env_def, Loader)
