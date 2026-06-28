# coding=utf-8
"""
Mock layer for NetEase SDK modules.
"""
import sys
import types


_ORIGINAL_MODULES = {}


class _FakeComponent(object):
    def __init__(self, name=''):
        self.__name = name

    def __getattr__(self, name):
        return lambda *a, **kw: None

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(_FakeComponent, self).__setattr__(name, value)
        else:
            object.__setattr__(self, name, value)


def _fake_get_component_cls():
    class _FakeCompCls(object):
        pass
    return _FakeCompCls


def _fake_get_engine_comp_factory():
    class _FakeFactory(object):
        def __getattr__(self, name):
            return lambda *a, **kw: _FakeComponent(name)
    return _FakeFactory()


def _fake_get_local_player_id():
    return '-1'


def _fake_get_level_id():
    return 'test-level-000'


def _fake_get_engine_namespace():
    return 'test_engine'


def _fake_get_engine_system_name():
    return 'test_system'


def _fake_get_system(namespace, name):
    return None


def _fake_register_system(namespace, name, cls_path):
    class _FakeSystem(object):
        def ListenForEvent(self, *a):
            pass
    return _FakeSystem()


def _fake_register_component(namespace, name, cls_path):
    return True


def _fake_create_component(entityId, namespace, compKey):
    return _FakeComponent(compKey)


def _fake_destroy_component(entityId, namespace, compKey):
    return True


def _fake_import_module(path):
    return None


def _fake_create_ui(namespace, name, params=None):
    return None


def _fake_get_screen_node_cls():
    class _FakeScreenNode(object):
        pass
    return _FakeScreenNode


def _fake_register_ui(namespace, name, cls_path, uiDef):
    return True


def _fake_get_server_system_cls():
    class _FakeServerSystem(object):
        pass
    return _FakeServerSystem


def _fake_get_client_system_cls():
    class _FakeClientSystem(object):
        pass
    return _FakeClientSystem


def _fake_get_custom_goal_cls():
    class _FakeGoalCls(object):
        pass
    return _FakeGoalCls


def _fake_get_server_tick_time():
    return 0


_FAKE_CLIENT_API = {
    'GetLocalPlayerId': _fake_get_local_player_id,
    'GetLevelId': _fake_get_level_id,
    'GetEngineNamespace': _fake_get_engine_namespace,
    'GetEngineSystemName': _fake_get_engine_system_name,
    'GetSystem': _fake_get_system,
    'RegisterSystem': _fake_register_system,
    'RegisterComponent': _fake_register_component,
    'CreateComponent': _fake_create_component,
    'DestroyComponent': _fake_destroy_component,
    'ImportModule': _fake_import_module,
    'GetComponentCls': _fake_get_component_cls,
    'GetEngineCompFactory': _fake_get_engine_comp_factory,
    'CreateUI': _fake_create_ui,
    'GetScreenNodeCls': _fake_get_screen_node_cls,
    'RegisterUI': _fake_register_ui,
    'GetClientSystemCls': _fake_get_client_system_cls,
    'GetServerSystemCls': _fake_get_server_system_cls,
}

_FAKE_SERVER_API = {
    'GetLocalPlayerId': _fake_get_local_player_id,
    'GetLevelId': _fake_get_level_id,
    'GetEngineNamespace': _fake_get_engine_namespace,
    'GetEngineSystemName': _fake_get_engine_system_name,
    'GetSystem': _fake_get_system,
    'RegisterSystem': _fake_register_system,
    'RegisterComponent': _fake_register_component,
    'CreateComponent': _fake_create_component,
    'DestroyComponent': _fake_destroy_component,
    'ImportModule': _fake_import_module,
    'GetComponentCls': _fake_get_component_cls,
    'GetEngineCompFactory': _fake_get_engine_comp_factory,
    'GetServerSystemCls': _fake_get_server_system_cls,
    'GetCustomGoalCls': _fake_get_custom_goal_cls,
    'GetServerTickTime': _fake_get_server_tick_time,
}


def install():
    _ORIGINAL_MODULES.clear()

    # Create parent packages with __path__ so mod.client etc resolve
    mod = types.ModuleType('mod')
    mod.__path__ = ['mod']
    sys.modules['mod'] = mod
    sys.modules.setdefault('mod', mod)

    client_pkg = types.ModuleType('mod.client')
    client_pkg.__path__ = ['mod.client']
    sys.modules['mod.client'] = client_pkg

    server_pkg = types.ModuleType('mod.server')
    server_pkg.__path__ = ['mod.server']
    sys.modules['mod.server'] = server_pkg

    common_pkg = types.ModuleType('mod.common')
    common_pkg.__path__ = ['mod.common']
    sys.modules['mod.common'] = common_pkg

    # Link parent -> child so import mod.client.xxx works
    mod.client = client_pkg
    mod.server = server_pkg
    mod.common = common_pkg

    client_mod = types.ModuleType('mod.client.extraClientApi')
    for k, v in _FAKE_CLIENT_API.items():
        setattr(client_mod, k, v)
    sys.modules['mod.client.extraClientApi'] = client_mod
    client_pkg.extraClientApi = client_mod  # 链接子模块到包

    server_mod = types.ModuleType('mod.server.extraServerApi')
    for k, v in _FAKE_SERVER_API.items():
        setattr(server_mod, k, v)
    sys.modules['mod.server.extraServerApi'] = server_mod
    server_pkg.extraServerApi = server_mod  # 链接子模块到包

    enum_mod = types.ModuleType('mod.common.minecraftEnum')
    sys.modules['mod.common.minecraftEnum'] = enum_mod


def uninstall():
    for name in (
        'mod.common.minecraftEnum',
        'mod.server.extraServerApi',
        'mod.client.extraClientApi',
        'mod.common',
        'mod.server',
        'mod.client',
        'mod',
    ):
        sys.modules.pop(name, None)
    _ORIGINAL_MODULES.clear()