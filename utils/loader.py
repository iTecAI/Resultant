import os
import importlib.machinery, importlib.util
from utils.plugin import Plugin

def load_plugin(path: str):
    loader = importlib.machinery.SourceFileLoader( 'plugin', path )
    spec = importlib.util.spec_from_loader( 'plugin', loader )
    _module = importlib.util.module_from_spec( spec )
    loader.exec_module( _module )
    return _module

def load_all(config: dict) -> dict[str, Plugin]:
    loc = config["plugins"]["pluginLocation"]
    to_load = config["plugins"]["pluginList"]
    plugins = {i: load_plugin(os.path.join(loc, i+".py")).PLUGIN(config["misc"]["userAgent"]) for i in to_load}
    return plugins