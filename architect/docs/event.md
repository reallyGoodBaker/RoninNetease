# 事件系统

## 概念

RoninNetease 提供三层事件抽象：

| 类型 | 用途 | 特性 |
|------|------|------|
| **EventSignal** | 简单观察者 | 一对多，按注册顺序同步执行 |
| **EventChain** | 可中断事件链 | 捕获/冒泡阶段，`stop()` 终止传递 |
| **ChainedEvent** | 事件对象 | 含 `stop()`/`prevent()`/`setEvent()` |

---

## EventSignal

```python
from architect.event.core import EventSignal

signal = EventSignal()
handler = lambda val: print('收到:', val)
signal.on(handler)
signal.emit(42)     # → 收到: 42
signal.off(handler)
```

---

## EventChain

```python
from architect.event.core import EventChain

chain = EventChain('MyEvent')
chain.guarded = True      # 前一个处理器异常 → 后续跳过
chain.useCapture = False  # False=冒泡（后注册先执行），True=捕获

# 捕获处理器（先注册先执行）
chain.capture(lambda ev: print('[Capture]', ev.dict()))
# 冒泡处理器（后注册先执行，子→父）
chain.addListener(lambda ev: print('[Bubble]', ev.dict()))

chain.dispatch({'key': 'value'})
```

---

## ChainedEvent

```python
def listener(self, event):
    # event 是 ChainedEvent 实例
    event.stop()            # 终止链（后续处理器不执行）
    event.prevent()         # 设置 cancel=True（引擎跳过默认行为）
    event.setEvent('h', 1) # 修改事件数据
    data = event.dict()     # 获取完整数据字典
```

---

## `@EventListener` 装饰器

```python
from architect.compact import EventListener

class DamageSystem(ServerSubsystem):

    @EventListener('EntityHurtEvent')
    def on_hurt(self, event):
        "event 是 ChainedEvent。"
        if event.damage > 100:
            event.prevent()

    @EventListener('EntityDeathEvent')
    def on_death(self, event):
        print('实体死亡:', event.entityId)
```

---

## 自定义事件 `@CustomEvent`

```python
from architect.compact import CustomEvent

class LevelSystem(ServerSubsystem):

    @CustomEvent('PlayerLevelUp')
    def on_level_up(self, event):
        pid = event.playerId
        lv = event.level
        self.sendClient(pid, 'ShowLevelUp', {'level': lv})
```

---

## 子系统内置事件方法

子系统中也提供了便捷的事件注册/注销 API：

```python
class MySystem(ServerSubsystem):

    def onInit(self):
        # 引擎事件（原生）
        self.listen('EntityHurtEvent', self.on_hurt)
        # 自定义事件
        self.on('PlayerLevelUp', self.on_level_up)
        # 广播自定义事件给所有监听者
        self.broadcast('GameStarted', {'time': 0})

    def onDestroy(self):
        self.unlisten('EntityHurtEvent', self.on_hurt)
        self.off('PlayerLevelUp', self.on_level_up)
```

---

## 兼容性提示

`ChainedEvent` 会自动处理引擎事件中的 `from` 字段：

```python
class ChainedEvent:
    def __init__(self, eventType, data={}, interruptRef=Ref(None)):
        if 'from' in data:
            data['source'] = data['from']  # 统一命名
```