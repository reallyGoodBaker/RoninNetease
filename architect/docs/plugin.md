# Plugin — 插件系统

插件系统提供了模块化的功能扩展机制，支持拓扑依赖排序、热升级和完整的生命周期钩子。

---

## 1. 架构

```
PluginBase (基类)
    ├── 用户自定义插件
    └── 系统插件（$vendor.*）
        ├── event        ← 事件系统封装
        ├── animation    ← 动画扩展（序列/蒙太奇）
        ├── input        ← 输入系统（键盘/鼠标映射）
        └── squad        ← 小队系统（实体分组管理）
```

---

## 2. 创建插件

### 2.1 基本结构

```python
from architect.core.loader import Plugin, PluginBase

@Plugin(
    name='MyPlugin',
    ver=[1, 0, 0],
    author='You',
    desc='My first plugin',
    deps={'OtherPlugin': '>=1.0.0'}
)
class MyPlugin(PluginBase):
    def onCreate(self):
        """插件实例创建时调用"""
        pass

    def onAttach(self, manager):
        """插件附加到 SubsystemManager 时调用"""
        pass

    def onReady(self, manager):
        """所有子系统就绪后调用"""
        pass

    def onRegisterComponent(self, compCls):
        """组件注册到引擎时调用，compCls 为组件类型列表"""
        pass

    def onAddSubsystem(self, subsystem):
        """有新子系统添加时调用"""
        pass

    def onRemoveSubsystem(self, subsystem):
        """有子系统移除时调用"""
        pass

    def onDestroy(self):
        """插件销毁时调用"""
        pass
```

### 2.2 `@Plugin` 参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `name` | `str` | 插件名称（唯一标识） |
| `ver` | `list[int]` | 版本号 `[major, minor, patch]`，如 `[1, 0, 0]` |
| `author` | `str` | 作者名 |
| `desc` | `str` | 插件描述 |
| `deps` | `dict \| None` | 依赖的其他插件，格式 `{'PluginName': '>=version'}` |

### 2.3 生命周期

```
@Plugin 装饰 → 创建 _PluginHost
    │
    ├── _PluginHost.create()
    │   └── plugin.onCreate()
    │
    ▼
_topologicalOrder(registerList) → 按依赖排序
    │
    ▼
_PluginHost.load(manager)
    └── plugin.onAttach(manager)
    │
    ▼
子系统就绪 → plugin.onReady(manager)
    │
    ▼
销毁 → plugin.onDestroy()
```

---

## 3. 插件依赖

### 3.1 声明依赖

```python
@Plugin(
    name='MyCombatPlugin',
    ver=[1, 0, 0],
    author='You',
    desc='Combat system',
    deps={
        'RoninAnimationEx': '>=1.0.0',
        'RoninInputEx': '>=1.0.0'
    }
)
class MyCombatPlugin(PluginBase):
    pass
```

### 3.2 拓扑排序加载

框架使用拓扑排序确保依赖插件先于依赖它们的插件加载：

```
依赖图: CombatPlugin → AnimationEx, InputEx
加载顺序: AnimationEx → InputEx → CombatPlugin
```

如果存在循环依赖，框架按注册顺序兜底加载，不会死循环。

### 3.3 获取其他插件

```python
from architect.core.loader import getPlugin, hasPlugin

class MyPlugin(PluginBase):
    def onReady(self, manager):
        if hasPlugin('RoninAnimationEx'):
            anim_plugin = getPlugin('RoninAnimationEx')
            # 使用动画插件的 API
```

---

## 4. 热升级

### 4.1 版本比较

当 `@Plugin` 声明的版本号高于当前已注册的版本时，框架自动执行热升级：

```python
# v1.0.1 升级到 v1.1.0
@Plugin(name='MyPlugin', ver=[1, 1, 0], author='You', desc='Upgraded')
class MyPlugin(PluginBase):
    pass
```

### 4.2 升级流程

1. 比较新版本号与已注册版本号（`compVer` 比较）
2. 若新版本更高 → 销毁旧实例（`onDestroy()`）
3. 创建新实例（`onCreate()`）
4. 重新附加到管理器（`onAttach()`）

---

## 5. 系统插件

### 5.1 启用插件

在 `conf.py` 中：

```python
PLUGINS = [
    '$vendor.event',       # 事件系统
    '$vendor.animation',   # 动画扩展
    '$vendor.input',       # 输入系统
    '$vendor.squad',       # 小队系统
]
```

### 5.2 事件系统插件 (`$vendor.event`)

封装了事件的分发和管理，推荐始终启用。

```python
# architect/plugins/event/client.py
class EventPlugin(PluginBase):
    def onCreate(self):
        # 初始化事件系统
        pass

# architect/plugins/event/server.py
class EventPluginServer(PluginBase):
    def onCreate(self):
        pass
```

### 5.3 动画扩展插件 (`$vendor.animation`)

**客户端：** `RoninAnimationEx`

提供动画序列和蒙太奇控制。用户通过实体变量控制动画：

```python
# 设置混合权重
entity.set_attr('blendex.{anim_name}', 0.5)

# 设置动画时间
entity.set_attr('anim_timeex.{anim_name}', 0.3)

# 设置通知
entity.set_attr('notify_{name}', 1)
```

**服务端：** `RoninAnimationExServer`

服务端动画同步插件。

### 5.4 输入系统插件 (`$vendor.input`)

**`RoninInputEx`** — 扩展的键盘/鼠标输入映射系统。

提供以下组件：
- `InputExComponent` — 输入状态组件
- `InputAction`, `InputValue` — 输入动作和值
- `MappingContext` — 输入映射上下文
- `Modifier`, `Trigger` — 修饰键和触发器
- `InputExEnums` — 输入枚举

**示例：**

```python
# 获取输入值
input_comp = getComponent(entityId, InputExComponent)
move_forward = input_comp.get('MoveForward')   # 0.0 ~ 1.0
is_jumping = input_comp.get('Jump')            # True/False
```

### 5.5 小队系统插件 (`$vendor.squad`)

实体分组管理，将实体加入/离开小队，支持小队内通信。

---

## 6. 用户插件

### 6.1 创建用户插件

用户插件位于模组根目录下的 `plugins/` 目录：

```
your_mod/
└── plugins/
    ├── __init__.py
    └── myPlugin.py
```

### 6.2 启用用户插件

在 `conf.py` 中以 `$user.` 前缀引用：

```python
PLUGINS = [
    '$vendor.event',
    '$user.myPlugin',    # → {modname}.plugins.myPlugin
]
```

### 6.3 插件路径解析

```python
# $vendor.{name} → architect.plugins.{name}
# $user.{name}   → {modname}.plugins.{name}

# 示例
'$vendor.animation' → 'architect.plugins.animation'
'$user.combat'      → 'my_mod.plugins.combat'
```

路径后自动追加 `.server` 或 `.client`：
```
architect.plugins.animation.client  (客户端)
architect.plugins.animation.server  (服务端)
```

---

## 7. 插件与子系统交互

### 7.1 捕获组件和子系统

当插件被导入时，框架使用 `ContextRecorder` 捕获其依赖的组件类型和子系统类型：

```python
class MyPlugin(PluginBase):
    def onAttach(self, manager):
        # manager 是 SubsystemManager 实例
        # 可以访问所有已注册的子系统
        mySystem = manager.getSubsystemByName('MySystem')

    def onRegisterComponent(self, compCls):
        # compCls 是组件类型列表
        for cls in compCls:
            print('Component registered:', cls.__name__)

    def onAddSubsystem(self, subsystem):
        print('Subsystem added:', subsystem.__class__.__name__)
```

### 7.2 注入依赖

插件在 `onAttach` 阶段可以通过 `SubsystemManager` 获取所需资源：

```python
class ConfigPlugin(PluginBase):
    def onAttach(self, manager):
        self.config = manager.bus.execute('get_config')
```

---

## 8. 插件加载流程详解

```
createServer() / createClient()
    │
    ▼
manager.INITIALIZED.on(lambda: _loadPlugins(manager, isHost))
    │
    ├── _scanPlugins(isHost)
    │   └── 遍历 PLUGINS 列表
    │       ├── 解析路径 ($vendor → architect.plugins, $user → {mod}.plugins)
    │       ├── 追加 .server 或 .client
    │       └── ImportModule(path)
    │           └── 模块导入触发 @Plugin 装饰器
    │               └── 创建 _PluginHost 并调用 onCreate()
    │
    └── _topologicalOrder(registerList)
        └── 按依赖排序后的顺序调用 host.load(manager)
            └── plugin.onAttach(manager)

manager.PRELOADED.on(lambda: _readyPlugins(manager))
    └── 每个插件调用 onReady(manager)
```

---

## 下一步

- [架构设计 (architecture.md)](architecture.md) — 整体架构理解
- [子系统 (subsystem.md)](subsystem.md) — 子系统 API
- [最佳实践 (best-practices.md)](best-practices.md) — 插件设计建议