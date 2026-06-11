# Event — 事件系统

RoninNetease 事件系统在网易引擎原生事件机制基础上，提供了责任链模式、装饰器注册和强类型事件对象。

---

## 1. 架构概览

```
architect.event
├── core.py          ← EventChain, ChainedEvent, EventSignal, EventTarget, Delegate
├── client.py        ← 客户端事件注册表（EventChain 实例池）
├── server.py        ← 服务端事件注册表
└── events/
    ├── player.py    ← 玩家相关事件
    ├── entity.py    ← 实体相关事件
    ├── block.py     ← 方块相关事件
    ├── item.py      ← 物品相关事件
    ├── world.py     ← 世界相关事件
    ├── control.py   ← UI 控制事件
    ├── interface.py ← UI 接口事件
    ├── lobby.py     ← 大厅事件
    ├── model.py     ← 模型相关事件
    ├── physx.py     ← 物理相关事件
    ├── setting.py   ← 设置相关事件
    ├── sound.py     ← 音效事件
    └── ui.py        ← UI 事件
```

---

## 2. 核心类

### 2.1 `ChainedEvent` — 事件对象

框架对引擎原生事件的包装，提供了统一的访问和中断接口：

```python
class ChainedEvent(object):
    def __init__(self, eventType, data={}, interruptRef=Ref(None))
    def stop()           # 停止事件传递
    def prevent()        # 取消默认行为（设置 cancel=True, ret=True）
    def setEvent(key, value)   # 修改事件字段
    def updateEvent(dict)      # 批量更新字段
    def dict()           # 获取内部 dict
    def clone()          # 克隆事件副本
    def __getattr__(name)  # 属性访问 → data[name]
```

**使用示例：**

```python
class MySystem(ServerSubsystem):
    @EventListener('EntityHurtEvent')
    def onEntityHurt(self, event):
        # 属性式访问
        entityId = event.id
        damage = event.damage
        source = event.srcId

        # 修改事件
        event.setEvent('damage', 0)

        # 停止传递
        if entityId == self.protected_id:
            event.stop()

        # 取消默认行为
        event.prevent()

        # 获取原始 dict
        raw = event.dict()
```

### 2.2 `EventChain` — 事件链（责任链模式）

```python
class EventChain(Unreliable):
    evType: str              # 事件类型名
    guarded: bool = True     # 是否保护模式（前序监听器异常则中断）
    useCapture: bool = False # 是否使用捕获模式

    def capture(fn)          # 添加捕获阶段监听器（先添加先执行）
    def addListener(fn)      # 添加冒泡阶段监听器（先添加后执行）
    def removeListener(fn)   # 移除监听器
    def dispatch(_ev)        # 分发事件
```

**执行顺序：**
- `useCapture=False`（默认）→ 逆序遍历 handlers（冒泡模式，后添加先执行）
- `useCapture=True` → 正序遍历 handlers（捕获模式，先添加先执行）
- `guarded=True`（默认）→ 任何 handler 抛异常，跳过后续 handler

### 2.3 `EventSignal` — 信号（观察者模式）

```python
class EventSignal(Unreliable):
    def on(fn)           # 注册处理器
    def off(fn)          # 注销处理器
    def emit(*args)      # 触发所有处理器
```

用于框架内部生命周期信号（`INITIALIZED`、`PRELOADED`）以及 Marker 的 `onEntityCreated`/`onEntityDestroyed`。

### 2.4 `Delegate` — 单回调委托

```python
class Delegate(Unreliable):
    def bind(fn)         # 绑定函数
    def call(*args)      # 调用
    def unbind()         # 解绑
    def __call__(*args)  # 可直接调用
```

### 2.5 `EventTarget` — 命名事件目标

```python
class EventTarget(object):
    def addListener(event, fn)    # 添加监听
    def removeListener(event, fn) # 移除
    def removeAllListener()       # 全部移除
    def dispatch(event, *args)    # 触发事件
```

---

## 3. 事件注册方式

### 3.1 `@EventListener` 装饰器（引擎事件）

```python
from architect.core import EventListener

class MySystem(ServerSubsystem):
    @EventListener('ServerPostInitEvent')
    def onServerPostInit(self, event):
        """引擎事件，event 为 ChainedEvent"""
        pass

    @EventListener('EntityHurtEvent')
    def onEntityHurt(self, event):
        entityId = event.id
        damage = event.damage
```

**装饰器签名：**

```python
def EventListener(eventType=None, isCustomEvent=False):
    """
    :param eventType: 事件类型字符串，None 则从默认事件类推断
    :param isCustomEvent: True 时为自定义事件，注册到自定义事件通道
    """
```

注册流程：
1. `@EventListener` 在方法上标记 `_event_listener` 注解
2. `Subsystem._init()` → `_addListeners()` 扫描所有带注解的方法
3. 通过 `Subsystem._addListener()` 注册到引擎事件系统

### 3.2 `@CustomEvent` 装饰器（自定义事件）

```python
from architect.core import CustomEvent

class MySystem(ClientSubsystem):
    @CustomEvent('MyDataSyncEvent')
    def onDataSync(self, event):
        data = event['data']
        print('Received:', data)
```

`@CustomEvent` 是 `@EventListener(eventType, isCustomEvent=True)` 的别名。

### 3.3 编程式注册

```python
class MySystem(ServerSubsystem):
    def onInit(self):
        # 自定义事件
        self.on('MyEvent', self.onMyEvent, isCustomEvent=True)

        # 引擎事件
        self.listen('EntityHurtEvent', self.onEntityHurt)

    def onMyEvent(self, event):
        pass

    def onDestroy(self):
        # 注销
        self.off('MyEvent', self.onMyEvent, isCustomEvent=True)
        self.unlisten('EntityHurtEvent', self.onEntityHurt)
```

---

## 4. 事件注册表 — `architect.event.client` / `architect.event.server`

框架为每种引擎事件类型维护了 `EventChain` 单例：

```python
from architect.event import event as eventClient  # 客户端
from architect.event import event as eventServer  # 服务端

# event 是 __getattr__ 拦截器，返回对应事件类型的 EventChain
chain = eventClient('EntityHurtEvent', isCustom=False)
chain.addListener(my_handler)
```

**`event` 对象的行为：**
- `event(name, isCustom)` — 获取或创建事件类型的 `EventChain`
- `event.has(name, isCustom)` — 检查事件类型是否已注册
- 属性访问 `event.SomeEvent` — 等同于 `event('SomeEvent', False)`

### 事件类型自动生成（可选）

框架在 `architect/event/events/` 下提供了预定义事件类文件，每个文件定义事件类型类：

```python
# architect/event/events/player.py
class ServerPlayerDieEvent:
    """玩家死亡事件"""
    pass

class EntityHurtEvent:
    """实体受伤事件"""
    pass
```

这些类可以通过 `EventListener` 的默认行为使用：
```python
@EventListener  # 不传 eventType，从默认参数的事件类推断
def onEntityHurt(self, event):
    pass
```

---

## 5. 事件分发流程

```
引擎事件触发
    │
    ▼
SubsystemManager.addListener() 或 Subsystem.on()
    │  调用 system.ListenForEvent(engine, sysName, eventType, listener, fn)
    │
    ▼
EventChain.dispatch(eventData)
    ├── 创建 ChainedEvent(eventType, eventData, interruptRef=Ref(None))
    ├── 按 capture/bubble 顺序遍历 handlers
    │   └── tryCall(handler, ChainedEvent)
    │       ├── handler 内调用 event.stop()
    │       │   → interruptRef.value = True → 中断后续 handler
    │       └── handler 内调用 event.prevent()
    │           → eventData['cancel'] = True
    │
    └── guarded=True 时，tryCall 捕获异常 → 停止传递
```

---

## 6. `EventSignal` 使用（生命周期信号）

```python
from architect.core.subsystem import SubsystemManager

manager = SubsystemManager.getInstance()

# 监听初始化完成
manager.INITIALIZED.on(lambda: print('Plugins loaded'))

# 监听预加载完成
manager.PRELOADED.on(lambda: print('All subsystems ready'))

# 注销
manager.INITIALIZED.off(callback)
```

---

## 7. 与 `@Sched.Event` 的区别

- `@EventListener` / `@CustomEvent` — 替换 `onUpdate` 等钩子，在事件发生时执行回调，回调接收 `ChainedEvent` 参数
- `@Sched.Event` — 调度器事件，在事件发生时将方法加入调度队列执行，**不接收**事件参数（事件数据通过 `EventReader` 组件获取）

```python
# 事件监听器（接收 ChainedEvent）
@EventListener('EntityHurtEvent')
def onHurt(self, event):
    target = event.id
    damage = event.damage

# 事件调度器（不接收参数，通过 EventReader 获取）
@Sched.Event('EntityHurtEvent')
def onHurtSched(self):
    reader = getComponent(self.entityId, EventReader)
    event = reader.ev
    target = event['id']
```

---

## 8. 最佳实践

1. **使用装饰器注册**，避免在 `onInit` 中手动调用 `self.on()`
2. **使用 `ChainedEvent` 属性访问**，它比 dict 访问更易读：
   ```python
   event.id  # 推荐
   event['id']  # 也支持
   ```
3. **在不需要中断事件流时不要调用 `stop()` 或 `prevent()`**
4. **自定义事件名称使用语义化前缀**，如 `OnPlayerLevelUp` 而非 `Ev1`
5. **客户端和服务端事件是分离的**，`@EventListener` 在服务端子系统中只监听服务端事件

---

## 下一步

- [调度系统 (scheduler.md)](scheduler.md) — 调度器完整 API
- [子系统 (subsystem.md)](subsystem.md) — 子系统生命周期
- [UI 系统 (ui.md)](ui.md) — 响应式 UI 数据绑定