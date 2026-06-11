# 插件系统

## 概念

插件是框架的扩展单元，可注册在 `PLUGINS` 配置列表中。每个插件由 `@Plugin` 装饰器标记，实现 `PluginBase` 的方法，拥有完整的生命周期钩子。

---

## 定义插件

```python
from architect.compact import Plugin, PluginBase

@Plugin('weather', ver=[1, 0, 0], author='Author', desc='天气系统插件')
class WeatherPlugin(PluginBase):

    def onCreate(self):
        "插件类实例化时调用。"
        pass

    def onAttach(self, manager):
        "框架初始化时调用。manager 是 SubsystemManager 实例。"
        pass

    def onReady(self, manager):
        "所有子系统创建完毕后调用。"
        pass

    def onRegisterComponent(self, compCls):
        "框架注册组件时调用。插件可以在此注入或替换组件。"
        pass

    def onAddSubsystem(self, subsystem):
        "框架添加子系统时调用。"
        pass

    def onRemoveSubsystem(self, subsystem):
        "框架移除子系统时调用。"
        pass

    def onDestroy(self):
        "插件被卸载时调用。"
        pass
```

---

## 在 `conf.py` 中启用插件

```python
# conf.py
PLUGINS = [
    '$vendor.weather',
    '$user.myPlugin',
]
# $vendor → architect/plugins/
# $user   → my_mod/plugins/
```

---

## 声明依赖 — v1.1.0

插件可以通过 `deps` 参数声明对其他插件的依赖。框架在加载时按拓扑排序执行，确保依赖项先加载。

```python
@Plugin('combat', ver=[1, 0, 0], deps={'weather': '>=1.0.0'})
class CombatPlugin(PluginBase):
    "combat 插件依赖 weather 插件 >= 1.0.0"
    pass
```

拓扑排序带循环依赖安全防护——出现循环时不会死循环，按注册顺序兜底加载。

---

## 运行时获取插件

```python
from architect.compact import getPlugin, hasPlugin

if hasPlugin('weather'):
    plugin = getPlugin('weather')
```