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

    def onRegisterComponent(self, manager, compCls):
        # type: (SubsystemManager, list[type]) -> None
        pass

    def onAddSubsystem(self, manager, subsystem):
        # type: (SubsystemManager, Subsystem) -> None
        pass

    def onRemoveSubsystem(self, manager, subsystem):
        # type: (SubsystemManager, Subsystem) -> None
        pass


_REGISTERED_PLUGINS = {} # type: dict[str, _PluginHost]
_LOADED_SERVER_PLUGINS = {} # type: dict[str, PluginBase]
_LOADED_CLIENT_PLUGINS = {} # type: dict[str, PluginBase]


def _plugins():
    return _LOADED_SERVER_PLUGINS if isServer() else _LOADED_CLIENT_PLUGINS

def getPlugin(name):
    # type: (str) -> PluginBase
    return _LOADED_SERVER_PLUGINS[name] if isServer() else _LOADED_CLIENT_PLUGINS[name]

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
    def __init__(self, name, author, desc, compCls):
        self.name = name
        self.author = author
        self.desc = desc
        self.compCls = compCls # type: type[PluginBase]
        self._inst = None

    def load(self, manager):
        # type: (SubsystemManager) -> None
        if self.name not in _REGISTERED_PLUGINS:
            raise Exception('Plugin {} not registered'.format(self.name))
        _LOADED_PLUGINS = _plugins()
        if self.name in _LOADED_PLUGINS:
            print('[INFO] Plugin {} already loaded')
            return
        _inst = self.compCls()
        _inst.onAttach(manager)
        _LOADED_PLUGINS[self.name] = _inst
        self._inst = _inst


def Plugin(name, author='Unknown', desc='Unknown'):
    def _decorator(cls):
        # type: (type) -> type
        if cls not in _REGISTERED_PLUGINS:
            _REGISTERED_PLUGINS[name] = _PluginHost(name, author, desc, cls)
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
    for _name in PLUGINS:
        _absPath = pluginPath(_name)
        if isServer():
            serverApi.ImportModule(_absPath)
        else:
            clientApi.ImportModule(_absPath)


def _loadPlugins(manager):
    # type: (SubsystemManager) -> None
    _scanPlugins()
    for _name, _host in _REGISTERED_PLUGINS.items():
        try:
            _host.load(manager)
            print('[INFO] Loaded plugin: ' + _host.name)
        except Exception as e:
            print('[ERROR] Failed to load plugin ' + _name)
    for _host in _LOADED_SERVER_PLUGINS.values():
        try:
            _host.onReady(manager)
        except Exception as e:
            print('[ERROR] Failed to ready plugin ' + _host.name)