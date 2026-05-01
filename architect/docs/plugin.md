# 插件系统 (architect.plugins)

提供可插拔的扩展机制。插件跟随子系统生命周期运行，支持 `$vendor`（框架内置）和 `$user`（用户自定义）两种来源。

## 注册插件

使用 `@Plugin` 装饰器注册一个插件：

```python
from architect.core.loader import Plugin, PluginBase

@Plugin(
    'MyPlugin',          # 插件名称（唯一标识）
    [ 1, 0, 0 ],         # 版本号 [major, minor, patch]
    'AuthorName',        # 作者
    'Description here'   # 插件描述
)
class MyPlugin(PluginBase):
    def onAttach(self, manager):
        # 插件加载时调用，此时子系统已创建
        pass

    def onReady(self, manager):
        # 所有子系统就绪后调用
        pass
```

## 启用插件

在 `architect/conf.py` 的 `PLUGINS` 列表中声明插件路径：

```python
PLUGINS = [
    # 框架内置插件（$vendor 前缀）
    '$vendor.animation',

    # 用户自定义插件（$user 前缀）
    '$user.my_plugin',

    # 纯模块路径
    'my_module.plugins.custom',
]
```

框架会自动为客户端和服务端加载对应的 `.client` / `.server` 模块。

## 获取插件

```python
from architect.core.loader import getPlugin, hasPlugin

# 检查插件是否已加载
if hasPlugin('MyPlugin'):
    plugin = getPlugin('MyPlugin')

# 调用插件暴露的静态方法
plugin.some_static_method()
```

## 内置插件：动画扩展 (RoninAnimationEx)

框架内置的 `animation` 插件提供动画序列与过渡控制。

### 动画时间缩放

```python
from architect.plugins.animation.client import AnimationExPlugin

# 设置全局动画时间缩放（值越大动画越快）
AnimationExPlugin.setDilation(2.0)   # 2倍速
AnimationExPlugin.setDilation(0.5)   # 0.5倍慢动作
AnimationExPlugin.setDilation(1.0)   # 恢复正常
```

### Molang 变量约定

该插件通过以下 Molang 变量控制动画：

| 变量 | 用途 |
|------|------|
| `v.blendex.<动画名>` | 控制动画混合权重（0~1） |
| `v.anim_timeex.<动画名>` | 控制动画时间进度 |
| `v.notify_<通知名>` | 定义通知触发（设为 1 触发，0 关闭） |