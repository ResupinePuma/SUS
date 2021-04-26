
import sys
from os.path import realpath, dirname, splitext, join
from requests import get
from imp import load_source
from sus.logger import Logger
import logging
import threading

logger = Logger('engines')

engine_dir = dirname(realpath(__file__))
engines = {}
engine_shortcuts = {}

def load_module(filename, module_dir):
    modname = splitext(filename)[0]
    if modname in sys.modules:
        del sys.modules[modname]
    filepath = join(module_dir, filename)
    module = load_source(modname, filepath)
    module.name = modname
    return module

def load_engine(engine_data):
    engine_module = engine_data
    try:
        engine = load_module(engine_module + '.py', engine_dir)
    except:
        logger.exception('Cannot load engine "{}"'.format(engine_module))
        return None
    return engine

def load_engines(engine_list: list = [] ):
    global engines
    engines.clear()
    engine_list.extend(["reddit","rss","telegram"])
    for engine_data in engine_list:
        engine = load_engine(engine_data)
        if engine is not None:
            engines[engine.name] = engine
    return engines