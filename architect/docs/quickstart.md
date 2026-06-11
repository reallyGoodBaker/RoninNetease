# Quickstart — 快速开始

本文从零开始引导你使用 RoninNetease 构建网易版《我的世界》模组，涵盖所有核心 API 和完整代码示例。

---

## 1. 环境要求

- **Python 2.7**（网易 MC 引擎使用 Python 2.7，不受用户控制）
- 网易《我的世界》开发者工具
- 一个模组工程项目

---

## 2. 项目结构

推荐的模组目录结构：

```
your_mod/
├── conf.py                # 用户配置（覆盖引擎默认配置）
├── modMain.py             # 模组入口
├── subsystems/            # 子系统目录
│   ├── __init__.py
│   └── mySystem.py
├── components/            # 自定义组件
│   └── health.py
├── plugins/               # 用户插件（可选）
└── architect/             # RoninNetease 框架（拷贝至此处）
```

---

## 3. 入口文件 — `modMain.py`

框架通过网易的 `Mod` 绑定类启动。`Mod.Binding` 声明模组名称和版本，`Mod.InitServer` / `Mod.InitClient` 分别在服务端和客户端初始化时调用：

```python
# -*- coding: utf-8 -*-
from mod.common.mod import Mod
from .engine.architect.startup import createServer, createClient, conf

@Mod.Binding(name=conf('MOD_NAME'), version=conf('MOD_VERSION'))
class ModBase(object):
    @Mod.InitServer()
    def initServer(self):
        createServer()

    @Mod.InitClient()
    def initClient(self):
        createClient()
```

`createServer()` 和 `createClient()` 会自动完成：
1. 创建 `SubsystemManager`
2. 扫描并导入配置中声明的模块列表
3. 触发 `INITIALIZED` 信号 → 导入并加载插件
4. 注册所有组件到引擎
5. 实例化所有用 `SubsystemServer` / `SubsystemClient` 装饰的子系统
6. 触发 `PRELOADED` 信号 → 调用所有子系统的 `onReady()` 和插件的 `onReady`
7. 启动 Tick 循环和 Render 循环

---

## 4. 配置文件 — `conf.py`

在模组根目录（`my_scripts/`）创建 `conf.py` 来覆盖框架默认配置：

```python
# -*- coding: utf-8 -*-

# 基础信息
MOD_NAME = 'my_mod'
MOD_VERSION = '1.0.0'

MOD_ENGINE_NAME = 'engine'   # 引擎系统名
MOD_SYSTEM_NAME = 'system'   # 子系统名

# 需要导入的模块（相对于 my_scripts 目录）
MOD_SERVER_MODULES = [
]
MOD_CLIENT_MODULES = [
]

# 启用的插件列表
PLUGINS = [
]
```

---

## 5. 创建第一个子系统

### 5.1 服务端子系统

```python
# subsystems/mySystem.py
from architect.core import SubsystemServer, ServerSubsystem, Sched
from architect.core import EventListener, CustomEvent

class MyServerSystem(ServerSubsystem):
    canTick = True  # 启用 onUpdate

    def onInit(self):
        """当前子系统创建完毕后调用"""
        print('[MySystem] Server initialized')

    def onReady(self):
        """所有子系统初始化完毕后调用，此时可获取其他子系统"""
        print('[MySystem] Server ready')

    def onUpdate(self, dt):
        """每 Tick 调用"""
        pass

    def onDestroy(self):
        """子系统销毁时调用"""
        pass

    # 注册引擎事件监听
    @EventListener('ServerPostInitEvent')
    def onServerPostInit(self, event):
        print('[MySystem] Server post init:', event)

    # 注册自定义事件监听
    @CustomEvent('MyCustomEvent')
    def onMyCustomEvent(self, event):
        print('[MySystem] Custom event received:', event)

    # 调度到 Tick 更新前
    @Sched.Tick(SchedUpdateFlags.BeforeUpdate)
    def beforeTick(self):
        pass

    # 广播事件到所有客户端
    def broadcastMessage(self, msg):
        self.sendAllClients('OnMessage', {'text': msg})

    # 生成实体
    def spawnNpc(self, template, pos, dim=0):
        from architect.core import Location
        loc = Location(pos, dim)
        return self.spawnEntity(template, loc, (0, 0))
```

### 5.2 客户端子系统

```python
# subsystems/myClientSystem.py
from architect.core import SubsystemClient, ClientSubsystem
from architect.core import Sched, EventListener

class MyClientSystem(ClientSubsystem):
    canTick = True

    def onInit(self):
        print('[MySystem] Client initialized')

    def onUpdate(self, dt):
        """每 Tick 调用"""
        pass

    def onRender(self, dt):
        """每渲染帧调用（仅客户端）"""
        pass

    @EventListener('OnMessage')
    def onMessage(self, event):
        print('[Client] Received:', event)
```

---

## 6. 使用装饰器注册子系统

框架支持装饰器自动注册：

```python
from architect.core import SubsystemServer, ServerSubsystem

@SubsystemServer  # 自动注册到 SubsystemManager
class MySystem(ServerSubsystem):
    canTick = True
```

模块在 `MOD_SERVER_MODULES` 中被声明后会被 Import，装饰器在此时自动生效。

---

## 7. 组件（Component）系统

### 7.1 定义组件

```python
from architect.component import Component, PersistKeys
from architect.component.schema import DefineFields, FieldSchema

# 简单组件
class Health(Component):
    hp = 100
    maxHp = 100

# 带持久化的组件
@PersistKeys('slots', 'selected')
class Inventory(Component):
    slots = [''] * 36
    selected = 0

# 带字段验证的组件
@DefineFields({
    'level': FieldSchema(default=1),
    'xp': FieldSchema(default=0,
                       validator=lambda v: v >= 0)
})
class PlayerStats(Component):
    pass
```

### 7.2 创建和获取组件

```python
from architect.component import createComponent, getOrCreateComponent
from architect.component import hasComponent, destroyComponent

# 创建组件
health = createComponent(entityId, Health)

# 获取已有组件
health = getOrCreateComponent(entityId, Health)
health.hp -= 10

# 检查组件是否存在
if hasComponent(entityId, Health):
    print('Entity has health')

# 销毁组件
destroyComponent(entityId, Health)
```

### 7.3 查询组件 — `@Query` 装饰器

`@Query` 接收组件类作为位置参数，`required` 和 `excluded` 作为可选关键字参数。用 `EntityId` 伪组件获取实体 ID：

```python
from architect.query import Query, EntityId

class PlayerDamageSystem(ServerSubsystem):
    canTick = True

    @Query(Health, EntityId,
           required=[PlayerStats],
           excluded=[Dead])
    def damagePlayer(self, healthComp, entityId):
        # healthComp: Health 组件实例
        # entityId: 实体 ID (str)
        # 注：required 中的 PlayerStats 仅用于筛选，不注入到参数
        healthComp.hp = max(0, healthComp.hp - 5)

    def onUpdate(self, dt):
        self.damagePlayer()  # 遍历所有匹配实体
```

`@Query` 接受的参数：
- `*compCls` — 位置参数，组件类列表，按顺序注入到方法参数中
- `required=[...]` — 必须存在的额外组件（不注入到参数中）
- `excluded=[...]` — 必须排除的组件

伪组件 `EntityId` 用于获取实体 ID，放在参数列表的任意位置即可。

---

## 8. 事件系统

### 8.1 监听引擎事件

```python
from architect.core import EventListener

class MySystem(ServerSubsystem):
    @EventListener('ServerPostInitEvent')
    def onServerPostInit(self, event):
        pass

    @EventListener('EntityHurtEvent')
    def onEntityHurt(self, event):
        entityId = event['id']
        cause = event['cause']
        damage = event['damage']
```

### 8.2 自定义事件

```python
from architect.core import CustomEvent

class MySystem(ClientSubsystem):
    @CustomEvent('MyDataSyncEvent')
    def onDataSync(self, event):
        data = event['data']
        print('Received:', data)
```

### 8.3 事件链 — `ChainedEvent`

事件监听器接收一个 `ChainedEvent` 对象：

```python
@EventListener('EntityHurtEvent')
def onEntityHurt(self, event):
    entityId = event.id          # 属性访问 → 等价于 event['id']
    damage = event.damage

    if entityId == self.adminId:
        event.stop()             # 停止事件向下传递
        event.setEvent('damage', 0)  # 修改事件数据
```

### 8.4 `ChainedEvent` API

| 方法 / 属性 | 说明 |
|---|---|
| `event.stop()` | 停止事件向下传递 |
| `event.prevent()` | 设置 `cancel=True`（阻止默认行为） |
| `event.setEvent(key, value)` | 修改事件属性 |
| `event.updateEvent(dict)` | 批量更新事件属性 |
| `event.dict()` | 获取事件的原始 dict |
| `event.clone()` | 克隆事件副本 |
| `event.<key>` | 通过属性访问事件字段 |

---

## 9. 调度系统 — `@Sched`

```python
from architect.core import Sched, SchedUpdateFlags

class MySystem(ServerSubsystem):
    # === Tick 调度 ===
    @Sched.Tick()  # 默认在 Update 阶段
    def onTickUpdate(self):
        pass

    @Sched.Tick(SchedUpdateFlags.BeforeUpdate)
    def beforeTick(self):
        pass

    @Sched.Tick(SchedUpdateFlags.AfterUpdate)
    def afterTick(self):
        pass

    # === 渲染帧调度（仅客户端） ===
    @Sched.Render()
    def onRender(self):
        pass

    # === 固定频率调度 ===
    @Sched.Fixed('MyFixedSched')
    def onFixedUpdate(self):
        pass

    def onReady(self):
        self.scheduleFixed('MyFixedSched', period=0.5)  # 0.5 秒

    # === 事件调度 ===
    @Sched.Event('EntityHurtEvent')
    def onEntityHurtSched(self):
        pass
```

---

## 10. UI 系统

```python
from architect.ui.client import UiSubsystem, UiDef, Sink, signal, Screen, AutoCreate, Hud

@UiDef('myHud')      # 类装饰器：声明 UI 命名空间
@Screen               # 类装饰器：标记为全屏界面
@AutoCreate           # 类装饰器：自动创建
class MyHUD(UiSubsystem):
    canTick = True

    def onCreate(self):
        """UI 创建时调用，等效于引擎 Create 事件"""
        # signal 返回 (getter, setter) 元组
        self.hpGet, self.hpSet = signal(100)
        self.nameGet, self.nameSet = signal('Steve')

        # 绑定控件
        label = self.find('/hpLabel')
        # ...

    @Sink  # 方法装饰器：无参数，自动追踪内部访问的所有 signal
    def refresh(self):
        """任何 signal 变化时自动调用"""
        hp = self.hpGet()
        name = self.nameGet()
        # 更新 UI 控件
        self.find('/hpLabel').SetText(str(hp))
```

**关键区别：** `signal()` 不是装饰器，返回 `(getter, setter)` 元组。`@Sink` 不带参数。`@UiDef`、`@Screen`、`@AutoCreate`、`@Hud` 都是类装饰器。

---

## 11. 插件系统

### 11.1 内置插件

框架内置了以下系统插件（`$vendor.*`）：

| 插件名 | 说明 | 标识符 |
|---|---|---|
| 事件系统 | 事件封装和分发 | `$vendor.event` |
| 动画扩展 | 动画序列和蒙太奇 | `$vendor.animation` |
| 输入系统 | 键盘/鼠标输入映射 | `$vendor.input` |
| 小队系统 | 实体分组管理 | `$vendor.squad` |

### 11.2 启用插件

```python
PLUGINS = [
    '$vendor.event',
    '$vendor.animation',
]
```

### 11.3 创建自定义插件

```python
# plugins/myPlugin.py
from architect.core.loader import Plugin, PluginBase

@Plugin(
    name='MyPlugin',
    ver=[1, 0, 0],
    author='You',
    desc='My first plugin',
    deps={'RoninAnimationEx': '>=1.0.0'}
)
class MyPlugin(PluginBase):
    def onCreate(self):
        print('[MyPlugin] Created')

    def onAttach(self, manager):
        print('[MyPlugin] Attached')

    def onReady(self, manager):
        print('[MyPlugin] Ready')

    def onDestroy(self):
        print('[MyPlugin] Destroyed')
```

在 `conf.py` 中启用：

```python
PLUGINS = [
    '$vendor.event',
    '$user.myPlugin',   # 用户插件路径: {modname}.plugins.myPlugin
]
```

---

## 12. 远程调用 (RPC)

```python
from architect.remote.common import Remote, remote

class SyncSystem(ServerSubsystem):
    @Remote
    def syncPlayerData(self, callerPlayerId, targetId=None, data=None):
        """被客户端远程调用时，第一个参数自动注入调用者的 playerId"""
        return {'status': 'ok'}

# === 客户端调用服务端 ===
class ClientCaller(ClientSubsystem):
    def onReady(self):
        # 无需返回值（fire-and-forget）
        remote.client.call('SyncSystem.syncPlayerData',
                           targetId='player123',
                           data={'hp': 100})

        # 需要返回值（返回 Future）
        fut = remote.client.invoke('SyncSystem.syncPlayerData',
                                    targetId='player123',
                                    data={'hp': 100})
        fut.done(lambda result: print('Success:', result))
        fut.expected(lambda err: print('Failed:', err))

# === 服务端调用客户端 ===
# remote.server.call(playerId, uri, *args, **kwargs)
# remote.server.callEvery(uri, *args, **kwargs)  # 广播
# remote.server.invoke(playerId, uri, *args, **kwargs)  # 需要返回值
```

---

## 13. Aspect 面向切面编程

```python
from architect.core.aspect import Before, After, AfterReturning, AfterThrowing, Replace
from architect.core.aspect import Aspect

@Aspect(SomeTargetClass)  # 将切面绑定到目标类
class MyAspect:
    @Before('someMethod')
    def beforeMethod(self, targetInst, args, kwargs):
        print('Before:', args)

    @After('someMethod')
    def afterMethod(self, targetInst, args, kwargs):
        print('After:', args)

    @AfterReturning('someMethod')
    def afterReturning(self, targetInst, returnVal, args, kwargs):
        print('Returned:', returnVal)

    @AfterThrowing('someMethod')
    def afterThrowing(self, targetInst, e, args, kwargs):
        print('Error:', e)

    @Replace('someMethod')
    def replaceMethod(self, targetInst, targetMethod, args, kwargs):
        print('Intercepted!')
        return targetMethod(targetInst, *args, **kwargs)
```

---

## 14. CommandBus — 命令总线

```python
from architect.core.subsystem import SubsystemManager

manager = SubsystemManager.getInstance()

# 注册命令处理器
def handleSpawn(template, location):
    print('Spawning:', template, 'at', location)
    return template

unreg = manager.bus.register('spawnNpc', handleSpawn)

# 执行命令（同步调用所有已注册的处理器）
results = manager.bus.execute('spawnNpc', 'zombie', (0, 64, 0))

# 注销
unreg()
```

---

## 15. Profiler 性能诊断

```python
from architect.core.profiler import profiler

with profiler.record('myOperation'):
    doHeavyWork()

# 获取快照（不重置）
snap = profiler.snapshot()
# {'myOperation': {'avgMs': 1.2, 'maxMs': 3.4, 'count': 60}}

# 获取快照并重置
snap = profiler.flush()
```

---

## 16. 统一导入入口 — `architect.compact`

```python
from architect.compact import *

# 即可使用所有核心 API：
# - SubsystemServer, SubsystemClient, ServerSubsystem, ClientSubsystem
# - Sched, Future, Async, EventListener, CustomEvent
# - Query, EntityId
# - createComponent, getComponent, hasComponent
# - LevelClient, LevelServer
# - UiDef, Sink, signal, Screen
# - AnnotationHelper
# - Remote
```

---

## 下一步

- [架构设计 (architecture.md)](architecture.md) — 理解框架的分层设计和数据流
- [子系统 (subsystem.md)](subsystem.md) — 深入子系统生命周期和通信
- [组件系统 (ecs.md)](ecs.md) — 完整的 ECS 文档
- [事件系统 (event.md)](event.md) — 事件 API 详解
- [最佳实践 (best-practices.md)](best-practices.md) — 开发建议和常见陷阱