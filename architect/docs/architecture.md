# Architecture — 架构设计

RoninNetease 是一个专为网易版《我的世界》设计的 ECS（Entity-Component-System）模组框架。本文档详细介绍其分层架构、核心设计决策和数据流。

这个框架不是为了让你更快地做出垃圾，而是为了让你有机会做出别人做不出来的东西。

---

## 1. 整体分层

```
┌─────────────────────────────────────────────────────────┐
│                    用户代码层                              │
│  subsystems/  components/  plugins/  conf.py  modMain.py │
├─────────────────────────────────────────────────────────┤
│                    Compact 入口层                         │
│              architect.compact (统一导出)                  │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│   UI     │  Event   │  Query   │ Remote   │   Aspect    │
│  系统     │  系统    │  系统    │  系统     │   系统      │
├──────────┼──────────┼──────────┼──────────┼─────────────┤
│              SubsystemManager (核心管理器)                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌───────────┐ │
│  │ Tick │ │Render│ │Fixed │ │CommandBus│ │ Profiler  │ │
│  │Sched │ │Sched │ │Sched │ │          │ │           │ │
│  └──────┘ └──────┘ └──────┘ └──────────┘ └───────────┘ │
├─────────────────────────────────────────────────────────┤
│                  引擎抽象层 (architect.core)               │
│  loader  │ basic │annotation│ configurator │ unreliable  │
├─────────────────────────────────────────────────────────┤
│                 网易 MC 引擎 API 层                        │
│   mod.client.extraClientApi / mod.server.extraServerApi   │
├─────────────────────────────────────────────────────────┤
│                    系统插件层                              │
│    event  │ animation │ input │ squad                    │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 模块职责矩阵

| 模块 | 路径 | 职责 |
|---|---|---|
| **core** | `architect/core/` | 核心基础设施：加载器、子系统管理器、调度器、命令总线、Profiler、Ref、AOP |
| **component** | `architect/component/` | ECS 组件系统：组件创建/销毁/查询、CompIndex 反向索引、持久化 |
| **event** | `architect/event/` | 事件系统：EventChain 责任链、ChainedEvent、EventSignal、引擎事件枚举 |
| **ui** | `architect/ui/` | UI 系统：UiSubsystem、Signal/Sink 响应式绑定、UiDef 声明式 UI、手势 |
| **math** | `architect/math/` | 数学库：vec3、vec4、mat4、Double、Vec3Utils |
| **level** | `architect/level/` | 关卡工具：LevelClient、LevelServer |
| **persistent** | `architect/persistent/` | 持久化数据管理 |
| **remote** | `architect/remote/` | 跨端 RPC：Remote 装饰器、callRemote、Future 异步 |
| **fsm** | `architect/fsm/` | 有限状态机：StateTree 树形状态机（推荐）、deprecated Classic FSM |
| **query** | `architect/query/` | 实体查询：Query 装饰器、CompIndex 缓存、QueryClient/QueryServer |
| **command** | `architect/command/` | 命令注册与管理 |
| **attr** | `architect/attr/` | 实体属性读写封装（客户端/服务端） |
| **utils** | `architect/utils/` | 工具集：设备信息、Molang、Persona、绘图、增强列表/函数 |
| **plugins** | `architect/plugins/` | 系统插件：事件、动画扩展、输入系统、小队系统 |
| **compact** | `architect/compact.py` | 统一导出入口，简化 import |

---

## 3. 核心设计决策

### 3.1 装饰器 vs 注册表

框架大量使用 Python 装饰器进行声明式注册，而非显式注册表调用。

**原因：**
- 减少样板代码，代码即文档
- 注册时机由框架控制，避免手动注册顺序错误
- 注解（annotation）机制统一管理元数据

**实现机制：**
框架通过 `AnnotationHelper` 在目标（类或方法）上以 `_annotation` 属性存储元数据字典。装饰器如 `@EventListener`、`@Sched.Tick`、`@Remote` 等通过 `AnnotationHelper.addAnnotation()` 标记目标，框架在合适时机（如子系统 `_init`）统一扫描并注册。

```
@EventListener('SomeEvent')     → 标记方法 → Subsystem._init() 扫描并注册
@Sched.Tick()                   → 标记方法 → Subsystem._init() 添加到 Scheduler
@Remote                         → 标记方法 → Subsystem._init() 注册到远程调用表
```

### 3.2 CompIndex 反向索引（vs Archetype）

ECS 的组件存储采用 **CompIndex（组件索引）** 模式：

- 每个组件类型维护一个 `{entityId: componentInstance}` 字典
- 查询时通过 CompIndex 缓存集合交集快速定位实体
- 相比 Archetype 模式（按组件组合排列实体），CompIndex 在组件种类多、实体数中等时更灵活且内存友好

**查询流程：**
1. `@Query(target='{Health,Transform}')` 被调用
2. 查询装饰器从 CompIndex 缓存获取 `Health` 的实体集合和 `Transform` 的实体集合
3. 取交集得到候选实体列表
4. 遍历候选实体，注入组件实例到方法参数

### 3.3 重入保护

`Scheduler` 实现了简单的重入保护机制：

- `executeSequence()` 在执行期间检查 `_sequenceExecuting` 标志
- 如果检测到重入（上一帧尚未完成），则递增 `_skippedUpdates` 计数器并跳过
- 这防止了因游戏帧率波动导致的任务堆积

### 3.4 Python 2.7 兼容策略

由于网易 MC 引擎运行在 Python 2.7 上，框架采取了以下策略：

- 所有源文件添加 `# coding=utf-8` 声明
- 使用 `FunctionType` / `GeneratorType` 代替 Python 3 的 `Callable` / `Iterator`
- 使用 `StopIteration` 的 `args[0]` 获取返回值（Py2 没有 `value` 属性）
- 不在源码中使用 semicolon

---

## 4. 启动流程

```
createServer() / createClient()
        │
        ▼
LoaderUtils.createManager()
        │
        ├── 获取/注册引擎 System 实例
        ├── 创建 SubsystemManager(system, engine, sysName)
        │       ├── 初始化 CommandBus
        │       ├── 初始化 TickScheduler
        │       ├── 初始化 RenderScheduler（仅客户端）
        │       └── 注册 Remote 调用接收器
        │
        ├── manager.createServer() / manager.createClient()
        │       │
        │       ├── [Server] 监听 LoadServerAddonScriptsAfter 事件
        │       │       └── 触发 → _initManager(isHost=True)
        │       │
        │       └── [Client] 直接调用 _initManager(isHost=False)
        │
        ▼
_initManager(isHost)
        ├── _importModules(isHost)     ← 导入 MOD_SERVER_MODULES / MOD_CLIENT_MODULES
        ├── INITIALIZED.emit()
        │       └── → _loadPlugins(manager, isHost)
        │               ├── _scanPlugins() 扫描并导入插件
        │               └── _topologicalOrder() 拓扑排序后调用 plugin.onAttach()
        │
        ├── _registerCompsIntoGame()    ← 注册所有 Component 到引擎
        ├── _addAnnotatedSubsystems()   ← 实例化 @SubsystemServer/@SubsystemClient 类
        │       └── 每个子系统调用 _init()
        │               ├── _addListeners()      注册事件监听
        │               ├── _addSchedMethods()   注册调度任务
        │               ├── _registerRemoteFuncs() 注册远程方法
        │               └── onInit()             用户初始化钩子
        │
        ├── _callReady(isHost)
        │       ├── 所有子系统调用 onReady()
        │       ├── 所有插件调用 onReady()
        │       └── PRELOADED.emit()
        │
        └── startTicking(isHost)
                ├── 监听 OnScriptTickServer / OnScriptTickClient
                └── 监听 GameRenderTickEvent（仅客户端）
```

---

## 5. Tick 循环

```
OnScriptTickServer / OnScriptTickClient 事件触发
        │
        ▼
SubsystemManager.tickSubsystem()
        ├── 遍历 subsystems，调用 onUpdate(dt)（canTick=True 的子系统）
        └── tickSched.executeSequence()
                ├── 执行 TIMER_TASK（超时/间隔任务）
                ├── 执行 BeforeUpdate 阶段任务
                ├── 执行 Update 阶段任务
                └── 执行 AfterUpdate 阶段任务
                        └── 返回 (deltaTime, skippedUpdates)

GameRenderTickEvent 触发（仅客户端）
        │
        ▼
SubsystemManager.tickRender()
        ├── 遍历 subsystems，调用 onRender(dt)
        └── renderSched.executeSequence()
```

---

## 6. 数据流

### 6.1 配置流

```
architect/conf.py (引擎默认配置)
        +
用户 conf.py (覆盖)
        │
        ▼
modConf() 合并函数
        ├── MOD_NAME / MOD_VERSION → 用户优先
        ├── PLUGINS / MOD_SERVER_MODULES → 取并集
        └── 其他 → 用户优先，HOT_RELOADABLE 白名单控制运行时修改
```

### 6.2 事件流

```
引擎事件 (OnScriptTickServer 等)
        │
        ▼
SubsystemManager.addListener() / Subsystem.on()
        │  通过 system.ListenForEvent 注册到引擎
        │
        ▼
引擎触发时 → EventChain.dispatch(event_data)
        ├── 创建 ChainedEvent(eventType, data, interruptRef)
        ├── 按 capture/bubble 顺序遍历 handlers
        │       └── handler(ChainedEvent)
        │               ├── event.stop() 设置 interruptRef → 停止传递
        │               └── event.prevent() 设置 cancel → 阻止默认
        └── guarded=True 时，handler 抛异常则跳过后续 handler
```

### 6.3 调度流

```
Scheduler._scheduleQueues = {
    'TimerTask':       [Task1, Task2, ...],
    'BeforeUpdate':    [Task3, ...],
    'Update':          [Task4, ...],
    'AfterUpdate':     [Task5, ...],
}
        │
        ▼
executeSequence()
        ├── 执行 TIMER_TASK
        ├── 执行 BeforeUpdate
        ├── 执行 Update
        └── 执行 AfterUpdate
```

---

## 7. 关键接口

### 7.1 SubsystemManager

`SubsystemManager` 是框架的中枢，通过单例模式管理：

```python
manager = SubsystemManager.getInstance()  # 获取当前端实例
manager.bus                                 # CommandBus
manager.getSubsystem(MySystem)             # 按类获取子系统
manager.getSubsystemByName('MySystem')     # 按名获取子系统
manager.tickSched                           # Tick 调度器
manager.renderSched                         # Render 调度器
manager.INITIALIZED                         # 初始化完成信号
manager.PRELOADED                           # 预加载完成信号
```

### 7.2 Subsystem 生命周期

```
实例化 → _init() → onInit() → onReady() → onUpdate(dt) [每帧] → onDestroy()
                                          → onRender(dt) [每帧, 客户端]
```

### 7.3 Plugin 生命周期

```
@Plugin 装饰 → 创建 _PluginHost
    → onCreate()          实例创建
    → onAttach(manager)   附加到管理器（拓扑排序后按顺序）
    → onReady(manager)    所有子系统就绪后
    → onDestroy()         销毁时
```

---

## 8. 扩展点

| 扩展方式 | 机制 |
|---|---|
| 自定义组件 | 继承 `Component`，用 `@DefineFields` 声明字段 |
| 自定义子系统 | 继承 `ServerSubsystem` / `ClientSubsystem`，用 `@SubsystemServer` / `@SubsystemClient` 注册 |
| 自定义插件 | 继承 `PluginBase`，用 `@Plugin` 装饰，通过 `PLUGINS` 配置启用 |
| AOP 切面 | 用 `@Aspect(TargetClass)` + `@Before/@After` 等装饰器 |
| 自定义调度器 | 使用 `SimpleFixedScheduler(period)` 或直接操作 `Scheduler` |
| 预设事件类型 | 在 `architect/event/events/` 下定义事件类 |

---

## 下一步

- [子系统 (subsystem.md)](subsystem.md) — 深入子系统 API
- [组件系统 (ecs.md)](ecs.md) — 完整的 ECS 参考
- [事件系统 (event.md)](event.md) — 事件系统详解
- [调度系统 (scheduler.md)](scheduler.md) — 调度器完整 API