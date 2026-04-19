if 1 > 2:
    from .subsystem import SubsystemManager, Subsystem

from ..conf import PLUGINS
from .basic import isServer, clientApi, serverApi
from .annotation import AnnotationHelper

class _ModuleLocator(object):
    pass


__modname__ = _ModuleLocator.__module__[:_ModuleLocator.__module__.find('.')]
__framework__ = __modname__ + '.architect'
__dirname__ = __framework__ + '.core'


class PluginBase(object):

    def onAttach(self, manager):
        # type: (SubsystemManager) -> None
        pass

    def onReady(self, manager):
        # type: (SubsystemManager) -> None
        pass

    def onRegisterComponent(self, compCls):
        # type: (list[type]) -> None
        pass

    def onAddSubsystem(self, subsystem):
        # type: (Subsystem) -> None
        pass

    def onRemoveSubsystem(self, subsystem):
        # type: (Subsystem) -> None
        pass


_REGISTERED_SER_PLUGINS = {} # type: dict[str, _PluginHost]
_REGISTERED_CLI_PLUGINS = {} # type: dict[str, _PluginHost]
_LOADED_SERVER_PLUGINS = {} # type: dict[str, PluginBase]
_LOADED_CLIENT_PLUGINS = {} # type: dict[str, PluginBase]


def _plugins():
    return _LOADED_SERVER_PLUGINS if isServer() else _LOADED_CLIENT_PLUGINS

def getPlugin(name):
    # type: (str) -> PluginBase
    return _LOADED_SERVER_PLUGINS[name] if isServer() else _LOADED_CLIENT_PLUGINS[name]

def hasPlugin(name):
    # type: (str) -> bool
    return name in _plugins()

def _notifyAddSubsystem(subsystem):
    # type: (Subsystem) -> None
    for _host in _plugins().values():
        _host.onAddSubsystem(subsystem)

def _notifyRemoveSubsystem(subsystem):
    # type: (Subsystem) -> None
    for _host in _plugins().values():
        _host.onRemoveSubsystem(subsystem)

def _notifyRegisterComponent(compCls):
    # type: (list[type]) -> None
    for _host in _plugins().values():
        _host.onRegisterComponent(compCls)


class _PluginHost(object):
    def __init__(self, name, ver, author, desc, compCls):
        self.name = name
        self.ver = ver
        self.author = author
        self.desc = desc
        self.compCls = compCls # type: type[PluginBase]
        self._inst = None

    def load(self, manager):
        # type: (SubsystemManager) -> None
        registerList = _REGISTERED_SER_PLUGINS if isServer() else _REGISTERED_CLI_PLUGINS
        if self.name not in registerList:
            raise Exception('Plugin {} not registered'.format(self.name))
        _LOADED_PLUGINS = _plugins()
        if self.name in _LOADED_PLUGINS:
            print('[INFO] Plugin {} already loaded')
            return
        _inst = self.compCls()
        _inst.onAttach(manager)
        _LOADED_PLUGINS[self.name] = _inst
        self._inst = _inst


def Plugin(name, ver=[0, 0, 1], author='Unknown', desc='Unknown'):
    def _decorator(cls):
        # type: (type) -> type
        registerList = _REGISTERED_SER_PLUGINS if isServer() else _REGISTERED_CLI_PLUGINS
        if cls not in registerList:
            registerList[name] = _PluginHost(name, ver, author, desc, cls)
        return cls
    return _decorator


VendorPlugins = __dirname__[:__dirname__.rfind('.')] + '.plugins'
UserPlugins = __modname__ + '.plugins'


def pluginPath(name):
    # type: (str) -> str
    return name.replace(
        '$vendor',
        VendorPlugins
    ).replace(
        '$user',
        UserPlugins
    ) + ('.server' if isServer() else '.client')


def _scanPlugins():
    getConf = modConf()
    for _name in getConf('PLUGINS'):
        _absPath = pluginPath(_name)
        if isServer():
            serverApi.ImportModule(_absPath)
        else:
            clientApi.ImportModule(_absPath)


def _loadPlugins(manager):
    # type: (SubsystemManager) -> None
    _scanPlugins()
    registerList = _REGISTERED_SER_PLUGINS if isServer() else _REGISTERED_CLI_PLUGINS
    for _name, _host in registerList.items():
        try:
            _host.load(manager)
            print('[INFO] Loaded plugin: ' + _host.name)
        except Exception as e:
            print('[ERROR] Failed to load plugin ' + _name)
    for _host in _plugins().values():
        try:
            _host.onReady(manager)
        except Exception as e:
            print('[ERROR] Failed to ready plugin ' + _host.name)


MOD_CONST_NAMES = [
    'MOD_NAME',
    'MOD_VERSION',
    'MOD_ENGINE_NAME',
    'MOD_SYSTEM_NAME',
]
MOD_ARRAYS = [
    'MOD_SERVER_MODULES',
    'MOD_CLIENT_MODULES',
    'PLUGINS',
]

def modConf():
    from .. import conf
    _confModule = serverApi.ImportModule(__modname__ + '.conf') if isServer() else clientApi.ImportModule(__modname__ + '.conf')
    engineConf = conf.__dict__
    userConf = _confModule.__dict__
    def getter(key):
        if key in MOD_CONST_NAMES:
            _user = userConf.get(key)
            if _user is None:
                return engineConf.get(key)
            return _user
        elif key in MOD_ARRAYS:
            _user = userConf.get(key)
            if _user is None:
                return getattr(conf, key)
            return set(engineConf.get(key) + _user)
        else:
            return None
    return getter