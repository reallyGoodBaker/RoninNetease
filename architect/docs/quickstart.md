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
│   └── my_system.py
├── components/            # 自定义组件
│   └── health.py
├── plugins/               # 用户插件（可选）
└── architect/             # RoninNetease 框架（拷贝至此处）
```

---

## 3. 入口文件 — `modMain.py`

框架的启动入口，只需要调用 `createClient()` 和 `createServer()`：

```python
# coding=utf-8
from architect.startup import createClient, createServer

# 服务端启动
createServer()

# 客户端启动
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

在模组根目录创建 `conf.py` 来覆盖框架默认配置：

```python
# coding=utf-8
# 基础信息
MOD_NAME = 'MyMod'
MOD_VERSION = '1.0.0'
MOD_ENGINE_NAME = 'MyModEngine'   # 引擎系统名
MOD_SYSTEM_NAME = 'MyModSystem'   # 子系统名

# 需要导入的模块（相对于模组根目录的路径）
MOD_SERVER_MODULES = [
    'subsystems.my_system',
]
MOD_CLIENT_MODULES = [
    'subsystems.my_system',
]

# 启用的插件列表
PLUGINS = [
    '$vendor.event',      # 事件系统插件（推荐启用）
]

# 热更配置白名单
HOT_RELOADABLE = {
    'MAX_PLAYERS',
    'DEBUG_MODE',
}
```

**配置覆盖规则：**
- `MOD_NAME`、`MOD_VERSION` 等单值配置 — 用户值优先
- `MOD_SERVER_MODULES`、`MOD_CLIENT_MODULES`、`PLUGINS` — 用户值与引擎值合并（取并集）
- 其他键 — 按 `HOT_RELOADABLE` 白名单控制运行时修改

---

## 5. 创建第一个子系统

### 5.1 服务端子系统

```python
# subsystems/my_system.py
from architect.core import SubsystemServer, ServerSubsystem, Sched
from architect.core import EventListener, CustomEvent
from architect.core import Internal

class MyServerSystem(ServerSubsystem):
    canTick = True  # 启用 onUpdate

    def onInit(self):
        """当前子系统创建完毕后调用"""
        print('[MySystem] Server initialized')

    def onReady(self):
        """所有子系统初始化完毕后调用，此时可获取其他子系统"""
        print('[MySystem] Server ready')
        # other = self.getManager().getSubsystem(AnotherSystem)

    def onUpdate(self, dt):
        """每 Tick 调用（每游戏帧）"""
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
    @Sched.Tick(Sched.Tick.BeforeUpdate)
    def beforeTick(self):
        pass

    # 广播事件到所有客户端
    def broadcast_message(self, msg):
        self.sendAllClients('OnMessage', {'text': msg})

    # 生成实体
    def spawn_npc(self, template, pos, dim=0):
        from architect.core import Location
        loc = Location(pos, dim)
        return self.spawnEntity(template, loc, (0, 0))
```

### 5.2 客户端子系统

```python
# subsystems/my_client_system.py
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

框架支持两种注册子系统的模式：

### 模式 1：装饰器注册（推荐）

```python
from architect.core import SubsystemServer, ServerSubsystem

@SubsystemServer  # 自动注册到 SubsystemManager
class MySystem(ServerSubsystem):
    canTick = True
```

### 模式 2：手动注册模块导入

服务端在 `MOD_SERVER_MODULES` 中声明了 `'subsystems.my_system'` 后，该模块会被 Import。子系统的 `@SubsystemServer` 装饰器会在此时自动调用。

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
class Inventory(Component):
    items = PersistKeys()          # 持久化字段列表
    slots = [''] * 36

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

```python
from architect.component import Query, EntityId, getComponent

class PlayerDamageSystem(ServerSubsystem):
    canTick = True

    @Query(
        target='{Health}',          # 需要 Health 组件
        required=['{PlayerStats}'], # 可选加载 PlayerStats
        attach_query=True           # 将查询结果传入参数
    )
    def damage_player(self, entityId, Health, PlayerStats=None):
        # entityId: 实体 ID (str)
        # Health: Health 组件实例
        # PlayerStats: PlayerStats 组件实例（可能为 None）
        Health.hp = max(0, Health.hp - 5)
        if PlayerStats:
            PlayerStats.xp += 1

    def onUpdate(self, dt):
        # 对所有拥有 Health 和 PlayerStats 的实体造成伤害
        self.damage_player()
```

`@Query` 的参数：
- `target` — 必须存在的组件（逗号分隔，如 `'{Health,Player}'`）
- `required` — 可选组件（允许为 `None`）
- `attach_query` — `True` 时自动传入 `entityId` + 组件实例作为参数；`False` 时在方法内通过 `getComponent()` 获取

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

事件监听器接收一个 `ChainedEvent` 对象，可以用它来中断事件流或修改事件数据：

```python
@EventListener('EntityHurtEvent')
def onEntityHurt(self, event):
    # event 是 ChainedEvent 实例
    entityId = event.id          # 属性访问 → 等价于 event['id']
    damage = event.damage

    if entityId == self.admin_id:
        event.stop()             # 停止事件继续传递
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
    # === Tick 调度（随游戏帧调度） ===

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
        # 在 onReady 中启动固定调度器（不要在 onInit 中调用）
        sched = self.scheduleFixed('MyFixedSched', period=0.5)  # 0.5 秒

    # === 事件调度 ===

    @Sched.Event('EntityHurtEvent', isCustom=False)
    def onEntityHurt(self):
        pass
```

---

## 10. UI 系统

```python
from architect.ui.client import UiSubsystem, UiDef, Sink, AutoCreate
from architect.ui.client import signal, Screen, Ui

class MyHUD(UiSubsystem):
    canTick = True

    @signal
    def hp(self):
        return self.health.hp  # 自动追踪 health.hp 的变化

    @UiDef('my_hud')  # UI JSON 中的命名空间
    @Screen('hud_screen')  # UI 屏幕名
    @AutoCreate
    def initHUD(self, ui: Ui):
        """UI 首次创建时调用"""
        self.hud = ui
        # 绑定 UI 控件数据
        self.hud.bind('hp_text', 'text', self.hp_signal)

    def onUpdate(self, dt):
        if self.hp_value != self.last_hp:
            self.last_hp = self.hp_value
            # signal 自动触发 UI 刷新
```

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

在 `conf.py` 中：

```python
PLUGINS = [
    '$vendor.event',
    '$vendor.animation',
]
```

### 11.3 创建自定义插件

```python
# plugins/my_plugin.py
from architect.core.loader import Plugin, PluginBase

@Plugin(
    name='MyPlugin',
    ver=[1, 0, 0],
    author='You',
    desc='My first plugin',
    deps={'RoninAnimationEx': '>=1.0.0'}  # 依赖其他插件
)
class MyPlugin(PluginBase):
    def onCreate(self):
        """插件实例创建时调用"""
        print('[MyPlugin] Created')

    def onAttach(self, manager):
        """插件附加到 SubsystemManager 时调用"""
        print('[MyPlugin] Attached')

    def onReady(self, manager):
        """所有插件加载完毕后调用"""
        print('[MyPlugin] Ready')

    def onDestroy(self):
        """插件销毁时调用"""
        print('[MyPlugin] Destroyed')
```

在 `conf.py` 中启用：

```python
PLUGINS = [
    '$vendor.event',
    '$user.my_plugin',   # 用户插件路径: {modname}.plugins.my_plugin
]
```

---

## 12. 远程调用 (RPC)

```python
from architect.remote.common import Remote, callRemote

class SyncSystem(ServerSubsystem):
    @Remote
    def sync_player_data(self, target_id=None, data=None):
        """可被客户端远程调用的方法"""
        # ... 处理逻辑
        return {'status': 'ok'}

class ClientCaller(ClientSubsystem):
    def onReady(self):
        # 调用服务端的 Remote 方法
        fut = callRemote('SyncSystem.sync_player_data',
                          target_id='player123',
                          data={'hp': 100})
        fut.done(lambda result: print('Success:', result))
        fut.expected(lambda err: print('Failed:', err))
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
        """方法调用前执行"""
        print('Before:', args)

    @After('someMethod')
    def afterMethod(self, targetInst, args, kwargs):
        """方法调用后执行"""
        print('After:', args)

    @AfterReturning('someMethod')
    def afterReturning(self, targetInst, returnVal, args, kwargs):
        """方法成功返回后执行"""
        print('Returned:', returnVal)

    @AfterThrowing('someMethod')
    def afterThrowing(self, targetInst, e, args, kwargs):
        """方法抛出异常后执行"""
        print('Error:', e)

    @Replace('someMethod')
    def replaceMethod(self, targetInst, targetMethod, args, kwargs):
        """完全替换原方法"""
        print('Intercepted!')
        return targetMethod(targetInst, *args, **kwargs)
```

---

## 14. CommandBus — 命令总线

```python
from architect.core.subsystem import SubsystemManager

manager = SubsystemManager.getInstance()

# 注册命令处理器
def handle_spawn(template, location):
    print('Spawning:', template, 'at', location)
    return template

unreg = manager.bus.register('spawn_npc', handle_spawn)

# 执行命令（同步调用所有已注册的处理器）
results = manager.bus.execute('spawn_npc', 'zombie', (0, 64, 0))
# results = ['zombie']

# 注销
unreg()
```

---

## 15. Profiler 性能诊断

```python
from architect.core.profiler import profiler

with profiler.record('my_operation'):
    do_heavy_work()

# 获取快照（不重置）
snap = profiler.snapshot()
# {'my_operation': {'avg_ms': 1.2, 'max_ms': 3.4, 'count': 60}}

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
# - vec3, mat4, Vec3Utils
# - LevelClient, LevelServer
# - UiDef, Sink, signal, Screen
# - AnnotationHelper
# - Remote, callRemote
```

---

## 下一步

- [架构设计 (architecture.md)](architecture.md) — 理解框架的分层设计和数据流
- [子系统 (subsystem.md)](subsystem.md) — 深入子系统生命周期和通信
- [组件系统 (ecs.md)](ecs.md) — 完整的 ECS 文档
- [事件系统 (event.md)](event.md) — 事件 API 详解
- [最佳实践 (best-practices.md)](best-practices.md) — 开发建议和常见陷阱