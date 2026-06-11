# Subsystem — 子系统

子系统（Subsystem）是 RoninNetease 框架中业务逻辑的基本组织单元。每个子系统封装一组相关功能，由 `SubsystemManager` 统一管理生命周期。

---

## 1. 类层次结构

```
Subsystem (base, abstract)
├── ServerSubsystem   ← 服务端子系统基类
└── ClientSubsystem   ← 客户端子系统基类
```

所有子系统必须继承 `ServerSubsystem` 或 `ClientSubsystem`，不能直接继承 `Subsystem`。

---

## 2. 创建子系统

### 2.1 装饰器注册（推荐）

```python
from architect.core import SubsystemServer, ServerSubsystem
from architect.core import Sched, EventListener, CustomEvent

@SubsystemServer  # 标记为服务端子系统，自动注册
class MySystem(ServerSubsystem):
    canTick = True

    def onInit(self):
        print('System initialized')

    def onReady(self):
        print('All systems ready')

    def onUpdate(self, dt):
        print('Tick:', dt)
```

```python
from architect.core import SubsystemClient, ClientSubsystem

@SubsystemClient  # 标记为客户端子系统，自动注册
class MyClientSystem(ClientSubsystem):
    canTick = True

    def onRender(self, dt):
        print('Render frame:', dt)
```

### 2.2 注册时机

`@SubsystemServer` / `@SubsystemClient` 装饰器在模块被 Import 时生效。装饰器内部调用 `LoaderUtils.getManager()` 获取当前 `SubsystemManager`，然后调用 `manager.registerSubsystem(cls)`。

**注意：** 装饰器调用时 `SubsystemManager` 必须已存在。如果通过 `modMain.py` 的 `createServer()` / `createClient()` 正常启动，管理器会在导入用户模块之前创建。

---

## 3. 生命周期

```
@SubsystemServer 装饰 → registerSubsystem(cls) [加入注册列表]
        │
        ▼
_initManager(isHost) → _addAnnotatedSubsystems()
        │
        ├── SubsystemManager.addSubsystem(cls)
        │       └── 实例化 cls(system, engine, sysName)
        │               └── _init()
        │                       ├── _addListeners()       扫描 @EventListener/@CustomEvent 并注册
        │                       ├── _addSchedMethods()    扫描 @Sched.* 并添加调度任务
        │                       ├── _registerRemoteFuncs()扫描 @Remote 并注册
        │                       └── onInit()              【用户钩子：子系统创建完毕】
        │
        ▼
_callReady(isHost)
        └── 所有子系统 onReady()    【用户钩子：所有子系统就绪，可跨系统通信】
        │
        ▼
startTicking(isHost) → tickSubsystem()
        └── 每帧调用 onUpdate(dt)   【用户钩子：游戏 Tick】（需 canTick=True）
        └── 每帧调用 tickSched.executeSequence()
                ├── TIMER_TASK
                ├── BeforeUpdate
                ├── Update
                └── AfterUpdate

[客户端] startTicking() → tickRender()
        └── 每帧调用 onRender(dt)   【用户钩子：渲染帧】
        └── 每帧调用 renderSched.executeSequence()

[销毁时]
        └── onDestroy()              【用户钩子：清理资源】
```

### 3.1 生命周期钩子

| 钩子 | 调用时机 | 用途 |
|---|---|---|
| `onInit()` | 子系统实例创建后立即调用 | 初始化内部状态，此时只有当前子系统可用 |
| `onReady()` | 所有子系统创建完毕后调用 | 跨子系统通信初始化，获取其他子系统引用 |
| `onUpdate(dt)` | 每游戏 Tick（需 `canTick=True`） | 游戏逻辑更新 |
| `onRender(dt)` | 每渲染帧（仅客户端） | 渲染相关逻辑 |
| `onDestroy()` | 子系统销毁时 | 清理资源 |

### 3.2 原子初始化

从 v1.1.0 开始，`Subsystem._init()` 实现了原子回滚：

如果在 `_addListeners()`、`_addSchedMethods()` 或 `_registerRemoteFuncs()` 中任一操作失败，已注册的资源会被自动清理，子系统从管理器中移除。这防止了"僵尸子系统"状态。

---

## 4. 核心属性

### Subsystem 基类属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `system` | `_ShadowSystemServer` \| `_ShadowSystemClient` | 引擎底层 System 实例 |
| `engine` | `str` | 引擎命名空间 |
| `sysName` | `str` | 引擎系统名称 |
| `ticks` | `int` | 已执行的 Tick 次数 |
| `canTick` | `bool` | 是否启用 `onUpdate` 回调（默认 `False`） |
| `initialized` | `bool` | 是否已初始化 |
| `fixedSchedulers` | `dict` | 已启动的固定频率调度器映射 |

---

## 5. 事件通信

### 5.1 监听引擎事件

```python
class MySystem(ServerSubsystem):
    @EventListener('ServerPostInitEvent')
    def onServerPostInit(self, event):
        """event 是 ChainedEvent 实例"""
        pass

    @EventListener('EntityHurtEvent')
    def onEntityHurt(self, event):
        entityId = event.id          # 等价于 event['id']
        damage = event.damage        # 等价于 event['damage']
```

### 5.2 监听自定义事件

```python
class MySystem(ClientSubsystem):
    @CustomEvent('MyDataSyncEvent')
    def onDataSync(self, event):
        data = event['data']
```

### 5.3 编程式监听

```python
class MySystem(ServerSubsystem):
    def onInit(self):
        # 自定义事件
        self.on('MyEvent', self.onMyEvent, isCustomEvent=True)
        # 引擎事件
        self.listen('EntityHurtEvent', self.onEntityHurt)

    def onMyEvent(self, event):
        pass

    def onEntityHurt(self, event):
        pass

    def onDestroy(self):
        self.off('MyEvent', self.onMyEvent, isCustomEvent=True)
        self.unlisten('EntityHurtEvent', self.onEntityHurt)
```

---

## 6. 跨端通信

### 6.1 服务端 → 客户端

```python
class MyServerSystem(ServerSubsystem):
    def sync_to_client(self, player_id):
        self.sendClient(player_id, 'OnSyncData', {'hp': 100})

    def broadcast(self):
        self.sendAllClients('OnGlobalEvent', {'message': 'hello'})
```

| 方法 | 说明 |
|---|---|
| `sendClient(targetIds, eventName, eventData)` | 发送给指定玩家（str 或 int 发单人，list 发多人） |
| `sendAllClients(eventName, eventData)` | 广播给所有客户端 |

### 6.2 客户端 → 服务端

```python
class MyClientSystem(ClientSubsystem):
    def send_to_server(self):
        self.sendServer('OnClientAction', {'action': 'jump'})
```

| 方法 | 说明 |
|---|---|
| `sendServer(eventName, eventData)` | 发送消息给服务端 |

### 6.3 广播事件

```python
# 在子系统内向自身监听的玩家广播（引擎层面）
self.broadcast('MyEvent', {'data': 42})
```

---

## 7. 实体操作

### 7.1 服务端

```python
class MyServerSystem(ServerSubsystem):
    def spawn(self):
        from architect.core import Location
        from architect.core import isServer
        # 按字符串模板生成
        entity_id = self.spawnEntity(
            'minecraft:zombie',
            Location((0, 64, 0), 0),
            (0, 0),           # rotation (yaw, pitch)
            isNpc=False,
            isGlobal=False
        )
        # 按 NBT 数据生成
        entity_id = self.spawnEntity(
            {'identifier': 'minecraft:zombie', 'nbt': {}},
            Location((0, 64, 0), 0),
            (0, 0)
        )

    def spawn_item(self):
        from architect.core import Location
        self.spawnItem(
            {'item': 'minecraft:diamond', 'count': 1},
            Location((0, 64, 0), 0)
        )

    def destroy(self, entity_id):
        self.destroyEntity(entity_id)
```

### 7.2 客户端

```python
class MyClientSystem(ClientSubsystem):
    def spawn(self):
        entity_id = self.spawnEntity(
            'minecraft:zombie',
            (0, 64, 0),    # pos
            (0, 0)         # rot
        )

    def destroy(self, entity_id):
        self.destroyEntity(entity_id)

    def create_effect(self):
        self.createSfx('effects/explosion', (0, 0, 0))
        self.createParticle('minecraft:flame', (0, 64, 0))
        self.createEffectBind('effects/heal', entityId, 'animation.stand')
        self.destroySfx(sfx_id)
```

---

## 8. 调度系统集成

```python
class MySystem(ServerSubsystem):
    canTick = True

    @Sched.Tick()
    def onTick(self):
        """每帧在 Update 阶段执行"""

    @Sched.Tick(SchedUpdateFlags.BeforeUpdate)
    def beforeUpdate(self):
        """在 Update 之前"""

    @Sched.Fixed('my_fixed')
    def onFixedUpdate(self):
        """固定频率执行"""

    def onReady(self):
        self.scheduleFixed('my_fixed', period=1.0)  # 1秒间隔

    @Sched.Event('EntityHurtEvent')
    def onEntityHurt(self):
        """事件触发时执行"""
```

`@Sched.Fixed` 注册的方法需要在 `onReady()` 中通过 `scheduleFixed()` 启动调度器。**不要**在 `onInit()` 中调用 `scheduleFixed()`，因为此时引擎尚未完全初始化。

---

## 9. 获取其他子系统

### 9.1 通过管理器

```python
class MySystem(ServerSubsystem):
    def onReady(self):
        manager = SubsystemManager.getInstance()
        other = manager.getSubsystem(OtherSystem)
        other.do_something()
```

### 9.2 通过静态工具类

```python
class MySystem(ServerSubsystem):
    def onReady(self):
        # 按类名获取
        other = SubsystemManager.getInstance().getSubsystemByName('OtherSystem')
```

### 9.3 通过子系统类方法

```python
other = OtherSystem.getInstance()  # 内部调用了 SubsystemManager
```

---

## 10. subsystem 静态工具类

`subsystem` 是一个静态工具类，代理「第一个注册的子系统」的常用方法。适合在未持有子系统引用时快速调用：

```python
from architect.core.subsystem import subsystem

# 客户端 → 服务端
subsystem.sendServer('MyEvent', {'data': 42})

# 服务端 → 指定客户端
subsystem.sendClient('player123', 'MyEvent', {'data': 42})

# 服务端 → 所有客户端
subsystem.sendAllClients('MyEvent', {'data': 42})

# 生成实体
subsystem.spawnServerEntity('minecraft:zombie', Location((0,64,0), 0), (0,0))
subsystem.spawnClientEntity('minecraft:zombie', (0,64,0), (0,0))

# 监听事件
subsystem.addListener('MyEvent', handler, isCustomEvent=True)
subsystem.removeListener('MyEvent', handler, isCustomEvent=True)
```

**注意：** `subsystem` 指向的是第一个被注册的子系统。如果模组有多个子系统，推荐通过 `SubsystemManager.getInstance().getSubsystem()` 获取精确的子系统实例。

---

## 11. Internal 标记

```python
from architect.core.subsystem import Internal

class MySystem(ServerSubsystem):
    @Internal
    def _privateHelper(self):
        """标记为内部方法，不会被框架处理为事件或调度"""
        pass
```

`@Internal` 装饰器在方法上设置 `_internal_method` 注解，阻止框架将其作为事件监听器或调度目标处理。

---

## 下一步

- [组件系统 (ecs.md)](ecs.md) — ECS 组件与查询
- [事件系统 (event.md)](event.md) — 完整的事件 API
- [调度系统 (scheduler.md)](scheduler.md) — 调度器详解
- [UI 系统 (ui.md)](ui.md) — 响应式 UI