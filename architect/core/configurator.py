# coding=utf-8
"""
引擎约束说明 (Engine Constraint Notes)

本文件与 architect/conf.py 构成双轨制配置体系，这是网易引擎 ImportModule
限制下的必要分层：

- 本文件提供运行时配置获取和热重载功能（modConf() getter/setter），
  它使用相对 import（from .... import conf）读取用户配置。
- 此 import 需要引擎 ImportModule 就绪后才能工作，因此本文件只能在
  SubsystemManager 初始化之后使用。
- 框架早期初始化（Loader 注册、插件扫描路径等）由 architect/conf.py
  提供配置，它通过 try/except import 在引擎加载前即可读取。

运行时热重载白名单（HOT_RELOADABLE）可通过用户 conf.py 扩展。
将两套系统合并为单一入口在现行引擎约束下不可行。
"""
class _ModuleLocator(object):
    pass


__modname__ = _ModuleLocator.__module__[:_ModuleLocator.__module__.find('.')]
__framework__ = __modname__ + '.engine.architect'
__dirname__ = __framework__ + '.core'


MOD_CONST_NAMES = [
    'ENGINE_MODULE_NAME',
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

# 允许在运行时通过 modConf().set(key, value) 修改的配置键
# 用户可在自己的 conf.py 中扩展此集合
HOT_RELOADABLE = set([
    # 'MAX_PLAYERS',
    # 'DEBUG_MODE',
    # 'LOG_LEVEL',
])

VendorPlugins = __dirname__[:__dirname__.rfind('.')] + '.plugins'
UserPlugins = __modname__ + '.plugins'


def modConf():
    from .. import conf
    engineConf = conf.__dict__  # type: dict[str, str | list[str]]
    try:
        from .... import conf as mUserConf
        userConf = mUserConf.__dict__  # type: dict[str, str | list[str]]
    except ImportError:
        raise ImportError(
            'Please create conf.py in the {} folder and define MOD_ENGINE_NAME and MOD_SYSTEM_NAME. '
            'If you already have a conf folder, define the two constants above in __init__.py'.format(__modname__)
        )

    # 合并用户定义的 HOT_RELOADABLE
    _hotReloadable = HOT_RELOADABLE.copy()
    userHot = userConf.get('HOT_RELOADABLE')
    if isinstance(userHot, (list, set)):
        _hotReloadable.update(userHot)

    def getter(key):
        # type: (str) -> str | list[str] | set[str] | None
        if key in MOD_CONST_NAMES:
            _user = userConf.get(key)  # type: ignore
            if _user is None:
                return engineConf.get(key)
            return _user
        elif key in MOD_ARRAYS:
            _user = userConf.get(key)  # type: ignore
            if _user is None:
                return engineConf.get(key)
            rawConf = engineConf.get(key)  # type: ignore
            if isinstance(_user, list) and isinstance(rawConf, list):
                return set(rawConf + _user)
        else:
            # 查找自定义热更键
            _user = userConf.get(key)
            if _user is not None:
                return _user
            return engineConf.get(key)
        return None

    def setter(key, value):
        # type: (str, object) -> None
        """
        运行时修改配置。仅允许修改 HOT_RELOADABLE 中列出的键。

        :param key:   配置键名
        :param value: 新值
        :raises RuntimeError: 若 key 不在 HOT_RELOADABLE 白名单中
        """
        if key not in _hotReloadable:
            raise RuntimeError(
                "Config '{}' is not hot-reloadable. "
                "Add it to HOT_RELOADABLE in your conf.py.".format(key)
            )
        existing = userConf.get(key)
        if existing is not None and type(value) != type(existing):
            raise TypeError("Config %s expects type %s, got %s"%(key,type(existing).__name__,type(value).__name__))
        userConf[key] = value

    getter.set = setter
    return getter