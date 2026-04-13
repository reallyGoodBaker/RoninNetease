# 事件核心 (Event Core) API

`architect.event.core` 模块是事件系统的核心实现，提供了事件委托、信号、目标、链式事件和事件链等基础类。

## `Delegate` 类

`Delegate` 类实现了简单的委托模式，用于绑定和调用单个函数。

### 继承

- 继承自 `Unreliable`（不可靠基类）。

### 构造函数

#### `__init__(self)`

初始化委托。

### 方法

#### `bind(self, fn)`

绑定函数到委托。

- **`fn`**: (可调用对象) 要绑定的函数。

#### `call(self, *args)`

调用绑定的函数。

- **`*args`**: (可变参数) 传递给函数的参数。

#### `unbind(self)`

解绑函数。

#### `__call__(self, *args)`

使委托对象可调用，等同于 `call(*args)`。

## `EventSignal` 类

`EventSignal` 类实现了信号-槽机制，支持多个处理函数。

### 继承

- 继承自 `Unreliable`。

### 构造函数

#### `__init__(self)`

初始化信号。

### 方法

#### `on(self, fn)`

添加处理函数。

- **`fn`**: (可调用对象) 处理函数。

#### `off(self, fn)`

移除处理函数。

- **`fn`**: (可调用对象) 要移除的处理函数。

#### `emit(self, *args)`

触发信号，调用所有处理函数。

- **`*args`**: (可变参数) 传递给处理函数的参数。

## `EventTarget` 类

`EventTarget` 类管理多个事件信号，提供事件监听和分发功能。

### 构造函数

#### `__init__(self)`

初始化事件目标。

### 方法

#### `addListener(self, event, fn)`

添加事件监听器。

- **`event`**: (字符串) 事件类型。
- **`fn`**: (可调用对象) 处理函数。

#### `removeListener(self, event, fn)`

移除事件监听器。

- **`event`**: (字符串) 事件类型。
- **`fn`**: (可调用对象) 要移除的处理函数。

#### `dispatch(self, event, *args)`

分发事件，触发对应事件的所有监听器。

- **`event`**: (字符串) 事件类型。
- **`*args`**: (可变参数) 传递给监听器的参数。

## `ChainedEvent` 类

`ChainedEvent` 类表示链式事件，支持事件传递控制和数据操作。

### 构造函数

#### `__init__(self, eventType, data={}, interruptRef=Ref(None))`

初始化链式事件。

- **`eventType`**: (字符串) 事件类型。
- **`data`**: (字典, 默认值 `{}`) 事件数据。
- **`interruptRef`**: (`Ref`, 默认值 `Ref(None)`) 中断引用，用于控制事件传递。

### 属性

#### `eventType`

- **类型**: 字符串
- **说明**: 事件类型。

### 方法

#### `stop(self)`

停止事件传递（设置中断引用为 `True`）。

#### `prevent(self)`

阻止默认事件（将 `cancel` 和 `ret` 字段设置为 `True`）。

#### `dict(self)`

获取事件数据的字典形式。

- **返回值**: (字典) 事件数据。

#### `setEvent(self, p, v)`

设置事件数据的字段。

- **`p`**: (字符串) 字段名。
- **`v`**: (任意) 字段值。

#### `updateEvent(self, updates)`

批量更新事件数据。

- **`updates`**: (字典) 要更新的字段映射。

#### `__getattr__(self, name)`

通过属性访问事件数据字段。

- **`name`**: (字符串) 字段名。
- **返回值**: 字段值，如果字段不存在则抛出 `AttributeError`。

#### `clone(self)`

克隆事件对象。

- **返回值**: (`ChainedEvent`) 新的事件对象。

## `EventChain` 类

`EventChain` 类管理事件监听器的顺序执行，支持捕获和冒泡模式。

### 继承

- 继承自 `Unreliable`。

### 构造函数

#### `__init__(self)`

初始化事件链。

### 属性

#### `guarded`

- **类型**: 布尔值
- **说明**: 当为 `True` 时，上一个事件监听器出错后，后续事件监听器将不会执行。

#### `useCapture`

- **类型**: 布尔值
- **说明**: 当为 `True` 时，事件监听器将按添加顺序执行（捕获模式）；否则按相反顺序执行（冒泡模式）。

### 方法

#### `capture(self, fn)`

添加事件监听器（捕获模式）。

- **`fn`**: (可调用对象) 处理函数。

#### `addListener(self, fn)`

添加事件监听器（冒泡模式）。

- **`fn`**: (可调用对象) 处理函数。

#### `removeListener(self, fn)`

移除事件监听器。

- **`fn`**: (可调用对象) 要移除的处理函数。

#### `dispatch(self, evType, _ev)`

分发事件，按顺序调用所有监听器。

- **`evType`**: (字符串) 事件类型。
- **`_ev`**: (字典) 事件数据。

## 装饰器函数

### `EventListener(eventType, isCustomEvent=False)`

事件监听器装饰器，用于标记方法为事件处理函数。

- **`eventType`**: (字符串) 事件类型。
- **`isCustomEvent`**: (布尔值, 默认值 `False`) 是否为自定义事件。

#### 示例

```python
from ..architect.event import EventListener

class MySystem:
    @EventListener('OnPlayerJoin')
    def on_player_join(self, ev):
        print('Player joined:', ev['player'])
```

### `CustomEvent(eventType)`

自定义事件装饰器，等同于 `EventListener(eventType, isCustomEvent=True)`。

- **`eventType`**: (字符串) 事件类型。

#### 示例

```python
from ..architect.event import CustomEvent

class MySystem:
    @CustomEvent('my_custom_event')
    def on_custom_event(self, ev):
        print('Custom event received:', ev)
```

## 使用示例

### 1. 使用 `Delegate`

```python
from ..architect.event import Delegate

def my_function(x, y):
    print(x + y)

delegate = Delegate()
delegate.bind(my_function)
delegate.call(10, 20)  # 输出 30
```

### 2. 使用 `EventSignal`

```python
from ..architect.event import EventSignal

signal = EventSignal()
signal.on(lambda x: print('Handler 1:', x))
signal.on(lambda x: print('Handler 2:', x))
signal.emit('test')  # 输出 Handler 1: test 和 Handler 2: test
```

### 3. 使用 `EventTarget`

```python
from ..architect.event import EventTarget

target = EventTarget()
target.addListener('click', lambda ev: print('Clicked:', ev))
target.dispatch('click', {'x': 100, 'y': 200})
```

### 4. 使用 `ChainedEvent`

```python
from ..architect.event import ChainedEvent
from ..ref import Ref

interrupt = Ref(False)
event = ChainedEvent('test', {'value': 42}, interrupt)
print(event.value)  # 输出 42
event.stop()  # 停止事件传递
```

### 5. 使用 `EventChain`

```python
from ..architect.event import EventChain

chain = EventChain()
chain.addListener(lambda ev: print('Listener 1:', ev))
chain.addListener(lambda ev: print('Listener 2:', ev))
chain.dispatch('test', {'data': 'hello'})
```
