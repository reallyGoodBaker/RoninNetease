# 事件系统

`architect` 提供了一套灵活的事件系统，支持引擎原生事件和自定义事件的监听与广播。

## 架构概览

事件系统由以下核心组件构成：

- **`EventChain`**: 事件链，管理同一事件类型的多个监听器
- **`EventSignal`**: 事件信号，轻量级的事件通知机制，适合响应式编程
- **`EventTarget`**: 事件目标，提供事件的添加/移除/广播能力
- **`CustomEvent`**: 自定义事件，封装了事件名称和选项
- **`Delegate`**: 委托，链式调用监听器集合

## 获取事件链

通过 `event()` 函数获取事件链实例：

```python
from architect.event.server import event as serverEvent
from architect.event.client import event as clientEvent

# 服务端事件链
ev = serverEvent('PlayerJoinEvent')

# 客户端事件链
ev = clientEvent('CustomEvent', isCustomEvent=True)
```

## 事件链 API

```python
chain = event('EventName', isCustomEvent=False)

# 添加监听器
chain.addListener(lambda ev: print("Event fired:", ev))

# 移除监听器
fn = lambda ev: print("remove me")
chain.addListener(fn)
chain.removeListener(fn)

# 分发事件
chain.dispatch({"key": "value"})

# 清空所有监听器
chain.clear()
```

## 事件信号 `EventSignal`

`EventSignal` 是轻量级的信号/槽机制，适合响应式数据绑定：

```python
from architect.event import EventSignal

signal = EventSignal()

def handler():
    print("Signal emitted!")

# 监听信号
signal.on(handler)

# 触发信号
signal.emit()

# 取消监听
signal.off(handler)
```

## 事件目标 `EventTarget`

`EventTarget` 提供封装的事件管理能力，适合作为基类使用：

```python
from architect.event import EventTarget

class MyClass(EventTarget):
    def __init__(self):
        EventTarget.__init__(self)
        self.listen('SomeEvent', self.on_event)

    def on_event(self, ev):
        print("Event received:", ev)

    def cleanup(self):
        self.removeAllListener()
```

### EventTarget 方法

- **`listen(event, handler)`**: 监听事件
- **`unlisten(event, handler)`**: 取消监听
- **`addListener(event, handler)`**: 监听事件
- **`removeListener(event, handler)`**: 取消监听
- **`removeAllListener()`**: 移除所有监听器
- **`dispatchEvent(event, args)`**: 广播事件

## 服务端全局事件

通过 `ServerEvents` 管理全局事件链：

```python
from architect.event.server import ServerEvents

chain = ServerEvents.getOrCreateChain('EventName', isCustomEvent=False)
chain.addListener(my_handler)
```

## 自定义事件

通过 `CustomEvent` 封装事件，支持自定义选项：

```python
from architect.event import CustomEvent

# 创建自定义事件
my_event = CustomEvent('MyEvent', option1=True)
my_event.dispatch({"data": 123})

# 监听
my_event.addListener(lambda e: print(e))
```

## 委托 / 链式调用

`Delegate` 用于封装一组可调用的监听器，支持链式操作：

```python
from architect.event import Delegate

del = Delegate(lambda: print("not implemented"))

# 添加调用
del += lambda: print("+ added callback")
del("hello")  # 调用