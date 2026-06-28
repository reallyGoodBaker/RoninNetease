# Loader — 框架加载器（底层机制）

Loader 是 RoninNetease 的**启动内核**，负责框架自身的引导、插件生命周期调度和子系统管理器创建。如果你需要深入理解框架如何启动、或者开发自己的插件，这一章会帮助你理解底层机制。

> 大多数模组开发者**不需要**直接接触 Loader。本章面向插件开发和框架定制场景。

---

## 1. 架构概览

```
启动入口（startup.py）
    │
    ├── createServer() ──→ LoaderUtils.createManager()
    │                       └── FrameworkLoaderServer.getLoader()
    │                           └── 向引擎注册 "RoninFramework.LoaderServer"
    │
    └── createClient() ──→ LoaderUtils.createManager()
                            └── FrameworkLoaderClient.getLoader()
                                └── 向引擎注册 "RoninFramework.LoaderClient"
```

Loader 在网易引擎层以**独立系统**的形式存在（`RoninFramework.LoaderServer` / `RoninFramework.LoaderClient`），与其他模组系统（`ModSubsystem`）分离。这种设计使得一个模组中可以存在多个独立的子系统管理器实例。

### 1.1 为什么 Loader 要与模组系统剥离？

网易引擎的模组系统存在以下限制：

- **系统注册是全局的**：引擎通过 `RegisterSystem(engineName, systemName, clsPath)` 注册，名称冲突会导致注册失败
- **一个模组只能有一个入口系统**：通常命名为 `ModSubsystem`，所有业务逻辑必须挂载在这个系统下
- **生命周期由引擎控制**：引擎在加载时自动实例化 `ModSubsystem`，开发者无法控制时机

如果将 Loader 嵌入 `ModSubsystem`，会带来三个问题：

**① 框架与用户代码耦合在同一系统中**

如果 Loader 和用户子系统都在 `ModSubsystem` 下运行，Loader 的初始化、错误处理和卸载会与用户代码互相干扰。一个子系统的异常可能影响 Loader 的信号分发，导致后续插件加载失败。

**② 限制了多管理器架构**

剥离后，`FrameworkLoader` 维护了 `{(engine, system): SubsystemManager}` 的映射表。这意味着同一个框架实例可以管理多个独立的子系统组——例如一个模组同时运行两个完全隔离的业务模块，各自拥有自己的插件、事件链和调度器。

```python
# 引擎层存在两个独立的系统
# RoninFramework.LoaderServer — 框架自身
# ModSubsystem                — 用户业务系统
#
# Loader 通过 _recordedSystems 可以同时管理多个:
loader.recordSystem('MyEngine', 'CombatSystem', combatManager)
loader.recordSystem('MyEngine', 'UISystem', uiManager)
```

**③ 框架升级不受模组生命周期约束**

Loader 作为 `RoninFramework` 命名空间下的独立系统，可以在 `ModSubsystem` 创建**之前**完成注册。这意味着框架的插件系统、配置读取和组件注册表可以在用户代码执行前全部就绪，用户可以放心地在 `@SubsystemClient` 装饰器中使用 `getComponent()` 等 API。

**对比：**
```
# 如果 Loader 嵌入 ModSubsystem（❌ 不推荐的设计）
ModSubsystem.__init__()
  ├── 用户子系统 A
  ├── 用户子系统 B
  ├── Loader 初始化（太晚了！插件可能错过 INITIALIZED 信号）
  └── ...

# 当前设计（✅）
FrameworkLoader.__init__()     ← 框架独立系统，最先初始化
  ├── 创建 SubsystemManager
  ├── 绑定 INITIALIZED / PRELOADED
  └── ModSubsystem 就绪后 → 触发用户子系统扫描
```

---

## 2. 核心类

### 2.1 `LoaderUtils` — 工具入口

```python
from architect.core.loader import LoaderUtils

# 获取当前端的 Loader 实例
loader = LoaderUtils.getLoader()

# 获取或创建当前模组的 SubsystemManager
manager = LoaderUtils.getManager()
manager = LoaderUtils.createManager()
```

| 方法 | 说明 |
|---|---|
| `getLoader()` | 获取 `FrameworkLoaderServer` 或 `FrameworkLoaderClient` 实例 |
| `getManager(engine, system)` | 获取指定 (引擎名, 系统名) 对应的 SubsystemManager |
| `createManager()` | 创建新的 SubsystemManager 并记录到 Loader |

### 2.2 `FrameworkLoaderServer` / `FrameworkLoaderClient`

这两个类继承自网易引擎的 `ServerSystem` / `ClientSystem`，作为框架在引擎层的**锚点**。它们维护了一个 `(engine, system) → SubsystemManager` 的映射表：

```python
class FrameworkLoaderServer(ServerSystem):
    _recordedSystems = {}  # {(engine, system): SubsystemManager}

    @classmethod
    def getLoader(cls):
        """获取或向引擎注册 Loader 系统"""
        loader = serverApi.GetSystem(RONIN_ENGINE, RONIN_SYSTEM_SER)
        if not loader:
            loader = serverApi.RegisterSystem(...)
        return loader

    def recordSystem(self, engine, system, manager):
        self._recordedSystems[(engine, system)] = manager

    def getManager(self, engine, system):
        return self._recordedSystems.get((engine, system))
```

### 2.3 `ContextRecorder` — 依赖追踪

`ContextRecorder` 是插件依赖管理的核心基础设施。它通过**模块级别的上下文栈**，在插件模块导入时自动记录该插件引用了哪些组件和子系统。

```python
from architect.core.contextRecorder import ContextRecorder, Context

# 框架在加载插件时自动使用：
depComps = ContextRecorder.get('depComps')        # 追踪组件依赖
depSubsystems = ContextRecorder.get('depSubsystems')  # 追踪子系统依赖

# 加载插件前：
depComps.start('architect.plugins.motion.client')   # 开启上下文
# ... import 插件模块（期间涉及的组件/子系统 import 会被记录）
depComps.stop()                                      # 关闭上下文
```

**工作原理：**
- `ContextRecorder.start(moduleName)` 将当前模块名推入上下文栈
- 当 `SubsystemClient` / `SubsystemServer` 装饰器被调用时，调用 `depSubsystems.record(subsystemCls)`，记录到所有活跃上下文中
- 插件卸载时，框架根据 `_capturedSubsystems` 自动移除对应子系统

### 2.4 `modConf()` — 配置访问器

```python
from architect.core.configurator import modConf

conf = modConf()
name = conf('MOD_NAME')          # 读取配置
conf.set('DEBUG_MODE', True)     # 运行时修改（仅限 HOT_RELOADABLE 白名单）
```

`modConf()` 返回一个 getter/setter 函数，遵循**用户覆盖引擎默认**的合并策略。`MOD_CONST_NAMES` 中的键直接覆盖，`MOD_ARRAYS` 中的键取并集。

---

## 3. `_PluginHost` — 插件托管

`_PluginHost` 是 `@Plugin` 装饰器背后的实现，负责插件实例的完整生命周期。

### 3.1 创建和依赖捕获

```python
class _PluginHost:
    name: str          # 插件名称
    compCls: type       # 插件类（继承 PluginBase）
    dependencies: dict  # 依赖声明 {'otherPlugin': '>=1.0.0'}
    _capturedComps: list      # 导入期间捕获的组件
    _capturedSubsystems: list # 导入期间捕获的子系统

    def create(self):
        """实例化插件，同时捕获其模块下导入的所有组件/子系统"""
        depComps.start(compModule)
        depSubsystems.start(compModule)
        try:
            _inst = self.compCls()
            _inst.onCreate()
        finally:
            depComps.stop()
            depSubsystems.stop()
        # 扫描所有 Context 记录，提取当前模块前缀下的组件/子系统
```

### 3.2 全生命周期图

```
@Plugin 装饰
    │
    ▼
_PluginHost.create()                   ← 插件类被 import 时立即执行
    ├── 开启 ContextRecorder 上下文
    ├── pluginCls()                     ← 实例化
    ├── plugin.onCreate()               ← 初始化钩子
    ├── 扫描并记录依赖的组件/子系统
    └── 关闭上下文
    │
    ▼
拓扑排序 _topologicalOrder()
    │  （按 deps 声明的依赖关系排序）
    │
    ▼
_PluginHost.load(manager)              ← SubsystemManager INITIALIZED 信号
    ├── plugin.onAttach(manager)        ← 附加钩子
    └── 注册到 _LOADED_PLUGINS
    │
    ▼
plugin.onReady(manager)                ← SubsystemManager PRELOADED 信号
    │                                   所有子系统就绪后
    │
    ▼
plugin.onDestroy()                     ← 热升级 / 模组卸载
    └── 移除 _capturedSubsystems
```

### 3.3 拓扑排序加载

```python
def _topologicalOrder(registerList):
    """
    对已注册插件按 deps 依赖关系进行拓扑排序。
    循环依赖时按注册顺序兜底，不会死循环。
    """
```

这意味着：

```python
@Plugin(name='A', deps={'B': '>=1.0.0'})
class PluginA(PluginBase): ...

@Plugin(name='B', deps={'C': '>=1.0.0'})
class PluginB(PluginBase): ...
```

加载顺序自动保证：**C → B → A**。

---

## 4. 启动流程全貌

RoninNetease 的启动由 `startup.py` 触发，最终执行到 `loader.py` 的 `createServer` / `createClient`：

```python
def createServer():
    manager = LoaderUtils.createManager()       # 1. 创建 SubsystemManager
    manager.INITIALIZED.on(lambda: _loadPlugins(manager, True))  # 2. 插件加载
    manager.PRELOADED.on(lambda: _readyPlugins(manager))         # 3. 插件就绪
    manager.createServer()                      # 4. 扫描 @SubsystemServer

def createClient():
    manager = LoaderUtils.createManager()
    manager.INITIALIZED.on(lambda: _loadPlugins(manager, False))
    manager.PRELOADED.on(lambda: _readyPlugins(manager))
    manager.createClient()
```

**完整时间线：**

```
1. modMain.py 调用 createServer() / createClient()
       │
2. LoaderUtils.createManager()
       ├── FrameworkLoader.getLoader() → 注册 Loader 系统
       ├── 注册 ShadowSystem（ModSubsystem）
       ├── new SubsystemManager(system, engine, systemName)
       └── 绑定 INITIALIZED / PRELOADED 信号
       │
3. manager.createServer() / createClient()
       ├── 扫描所有 @SubsystemServer/@SubsystemClient 装饰的子系统
       ├── 拓扑排序子系统 deps
       ├── 依次调用 subsystem._init()
       │   ├── _addListeners()    扫描 @EventListener
       │   ├── _addSchedMethods() 扫描 @Sched.*
       │   └── _registerRemoteFuncs() 扫描 @Remote
       └── 触发 PRELOADED 信号
       │
4. _loadPlugins(manager, isHost)
       ├── _scanPlugins() → 按 conf.PLUGINS 导入插件模块
       ├── _topologicalOrder() → 按依赖排序
       └── 依次 _host.load(manager) → plugin.onAttach()
       │
5. _readyPlugins(manager)
       └── 遍历所有已加载插件 → plugin.onReady()
```

---

## 5. 模块关联 — Loader 如何串联整个框架

Loader 是框架的**中央调度员**，它不直接实现业务功能，而是负责协调其他核心模块的初始化和生命周期。

### 5.1 关系总览

```
                        createServer() / createClient()
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
             SubsystemManager  PluginHost     Profiler
             (subsystem.py)  (loader.py)  (profiler.py)
                    │             │             │
          ┌─────────┼──────┬──────┤             │
          ▼         ▼      ▼      ▼             │
     Component  Scheduler Event  Bus            │
  (component/) (scheduler (event/ (bus.py)      │
                .py)      core.py)              │
          │         │      │      │             │
          └─────────┴──────┴──────┴─────────────┘
                         │
                    modConf()
                  (configurator.py)
```

### 5.2 Loader → SubsystemManager

Loader 是 SubsystemManager 的**唯一创建者**。所有管理器的创建都经过 `LoaderUtils.createManager()`：

```python
# loader.py
def createServer():
    manager = LoaderUtils.createManager()        # ← 创建管理器
    manager.INITIALIZED.on(lambda: _loadPlugins(manager, True))
    manager.PRELOADED.on(lambda: _readyPlugins(manager))
    manager.createServer()                        # ← 触发子系统扫描

# subsystem.py
class SubsystemManager:
    def createServer(self):
        # ...
        self.system.ListenForEvent(..., 'LoadServerAddonScriptsAfter', ...)
        # ↑ 监听引擎事件 → _initManager() → 扫描所有 @SubsystemServer
```

SubsystemManager 在构造函数中初始化了所有核心子模块：

```python
class SubsystemManager:
    def __init__(self, system, engine, sysName):
        self.INITIALIZED = EventSignal()   # ← event/core.py
        self.PRELOADED = EventSignal()     # ← event/core.py
        self.bus = CommandBus()            # ← core/bus.py
        self.renderSched = Scheduler()     # ← core/scheduler.py
        self.tickSched = Scheduler()       # ← core/scheduler.py
        # ... remote calls registration
```

### 5.3 Loader → Plugin

Plugin 的加载完全由 Loader 驱动：

| 步骤 | Loader 动作 | Plugin 钩子 |
|---|---|---|
| `@Plugin` 装饰时 | 创建 `_PluginHost` 并调用 `_host.create()` | `onCreate()` |
| `INITIALIZED` 信号 | `_loadPlugins(manager)` → `_host.load(manager)` | `onAttach(manager)` |
| `PRELOADED` 信号 | `_readyPlugins(manager)` | `onReady(manager)` |

插件通过 `ContextRecorder` 自动追踪依赖，卸载时 Loader 负责清理：

```python
# loader.py
class _PluginHost:
    def destroy(self):
        self._inst.onDestroy()
        if self._capturedSubsystems:
            for _sys in self._capturedSubsystems:
                LoaderUtils.getManager().removeSubsystem(_sys)  # ← 通过 Loader 获取管理器
```

### 5.4 Loader → Component

组件注册链：**Loader → SubsystemManager._initManager() → `_registerCompsIntoGame()`**

```python
# subsystem.py
def _initManager(self, isHost):
    self._importModules(isHost)
    self.INITIALIZED.emit()
    self._preloaded = True
    _registerCompsIntoGame(isHost)   # ← 将所有 @Component 注册到引擎
    # ...
```

```python
# component/core.py
def _registerCompsIntoGame(isHost):
    '''将所有已声明的 Component 注册到引擎'''
    # compIndex、NeC/NeS 别名等都在此阶段绑定
```

`@Component` 装饰器本身在 import 时就注册了类型信息，但**实际的引擎级注册**发生在 `_initManager` → `_registerCompsIntoGame` 中。这意味着：

> 组件类型可以在任意模块中声明，但只有在管理器初始化后才能使用 `getComponent()` 等方法获取实例。

### 5.5 Loader → Event

Loader 本身不使用事件系统，但它创建的 `SubsystemManager` 暴露了两个核心信号：

```python
manager.INITIALIZED   # EventSignal — 模块导入完成，插件尚未加载
manager.PRELOADED     # EventSignal — 所有子系统就绪，插件 onReady 已调用
```

**时间线：**
1. `manager.INITIALIZED.emit()` → **此时** `@EventListener` 装饰的方法已注册但尚未收到事件（引擎事件需要引擎触发）
2. `_loadPlugins(manager)` → 插件 `onAttach()` 
3. `manager.PRELOADED.emit()` → `_readyPlugins(manager)` → 插件 `onReady()`

在 `manager.PRELOADED` 之后，所有子系统的 `@EventListener`、`@Sched.*`、`@Remote` 都已就位，可以接收引擎事件。

### 5.6 Loader → Scheduler

Scheduler 由 SubsystemManager 持有，Loader 通过管理器间接控制调度器的启停：

```python
# subsystem.py
def startTicking(self, isServer):
    # 注册引擎 Tick 事件
    self.system.ListenForEvent(..., 'OnScriptTickServer', self.tickSubsystem)
    self.system.ListenForEvent(..., 'OnScriptTickClient', self.tickSubsystem)
    # 客户端额外注册渲染 Tick
    self.system.ListenForEvent(..., 'GameRenderTickEvent', self.tickRender)

def tickSubsystem(self):
    # 驱动 tickSched 和 renderSched（仅客户端）
    self.tickSched._tick()
    if not isServer():
        self.renderSched._tick()
    profiler.feedSched('tick', self.tickSched)   # ← 连接 Profiler
```

### 5.7 Loader → Profiler

Profiler 通过 Loader 串联到 Scheduler 的 Tick 循环中。Scheduler 跳过帧时自动记录到 Profiler：

```python
# profiler.py — 全局单例
profiler = Profiler()

# subsystem.py — 在 tick 循环中调用
profiler.feedSched('tick', self.tickSched)
```

用户通过 `modConf().set()` 可以动态开关 Profiler：
```python
conf = modConf()
conf.set('PROFILER_ENABLED', False)
```

### 5.8 Loader → Startup → 用户入口

从用户视角看，整个框架的入口只需两行：

```python
# modMain.py
from architect.startup import createServer, createClient

# startup.py 只是 loader 的别名导出
from .core.loader import createClient, createServer
```

这个极简的入口背后，Loader 完成了上述所有模块的初始化。用户无需关心加载顺序，`@SubsystemClient`、`@Plugin`、`@Component` 等装饰器会按照正确的时机被 Loader 发现和执行。

---

## 6. `SubsystemClient` / `SubsystemServer` 装饰器

这两个装饰器是**自动注册子系统**的快捷方式，底层依赖 Loader：

```python
from architect.core.loader import SubsystemClient

@SubsystemClient
class MyClientSystem(ClientSubsystem):
    def onCreate(self):
        pass
```

**内部实现：**

```python
def SubsystemClient(subsystemCls):
    manager = LoaderUtils.getManager()
    if not manager:
        raise RuntimeError('SubsystemManager 尚未创建')
    if not isServer():
        depSubsystems.record(subsystemCls)  # 记录到当前活跃的插件上下文
        manager.registerSubsystem(subsystemCls)
    return subsystemCls
```

> **注意：** `@SubsystemClient` / `@SubsystemServer` 必须在 `createServer()` / `createClient()` 执行**之后**才能工作（因为需要 SubsystemManager 已创建）。框架通过 `startup.py` 控制顺序来保证这一点。

---

## 7. 自定义启动流程

如果你需要完全控制框架的启动顺序（例如在多个模组间共享 Loader），可以直接使用 `LoaderUtils`：

```python
from architect.core.loader import LoaderUtils, _loadPlugins, _readyPlugins, SubsystemManager

# 手动创建管理器
manager = LoaderUtils.createManager()

# 注册子系统
manager.registerSubsystem(MySystemA)
manager.registerSubsystem(MySystemB)

# 手动初始化
manager.initAllSubsystems()

# 手动加载插件
_loadPlugins(manager, isHost=True)
_readyPlugins(manager)
```

也可以通过 `LoaderUtils.getManager()` 获取**其他引擎系统**中的 SubsystemManager：

```python
loader = LoaderUtils.getLoader()
otherManager = loader.getManager('OtherEngine', 'OtherSystem')
```

---

## 8. 配置与热重载

`modConf()` 支持运行时修改白名单内的配置：

```python
from architect.core.configurator import modConf, HOT_RELOADABLE

conf = modConf()

# 在用户 conf.py 中扩展白名单：
HOT_RELOADABLE.update(['MAX_PLAYERS', 'DEBUG_MODE'])

# 运行时修改：
conf.set('DEBUG_MODE', True)  # 需要先加入白名单
```

---

## 下一步

- [插件系统 (plugin.md)](plugin.md) — `@Plugin` 装饰器的使用方式
- [子系统 (subsystem.md)](subsystem.md) — SubsystemManager 生命周期
- [架构设计 (architecture.md)](architecture.md) — 整体架构决策