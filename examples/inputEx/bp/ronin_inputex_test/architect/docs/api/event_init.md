# 事件模块 (`__init__.py`)

`architect.event.__init__.py` 是事件系统的入口模块，它从 `.core` 子模块导出了核心事件相关的类和装饰器。

## 导入的类

该模块从 `.core` 子模块导入了以下类：

- **`CustomEvent`**: 自定义事件类，用于创建和触发自定义事件。
- **`EventListener`**: 事件监听器装饰器，用于标记方法为事件处理函数。
- **`Delegate`**: 委托类，用于实现事件回调机制。
- **`EventChain`**: 事件链类，用于管理事件的顺序执行。
- **`EventSignal`**: 事件信号类，用于实现信号-槽机制。
- **`EventTarget`**: 事件目标类，用于管理事件监听器。
- **`ChainedEvent`**: 链式事件类，用于支持事件链的传递。

## 使用示例

```python
from ..architect.event import CustomEvent, EventListener

# 创建自定义事件
my_event = CustomEvent('my_event')

# 使用事件监听器装饰器
class MySystem:
    @EventListener('my_event')
    def on_my_event(self, ev):
        print('Event received:', ev)
```

## 说明

这些类提供了完整的事件系统功能，包括：

1. **事件定义与触发**：通过 `CustomEvent` 创建和触发事件。
2. **事件监听**：通过 `EventListener` 装饰器注册事件处理函数。
3. **事件委托**：通过 `Delegate` 实现回调机制。
4. **事件链**：通过 `EventChain` 和 `ChainedEvent` 管理事件的顺序执行和传递。
5. **事件信号**：通过 `EventSignal` 实现发布-订阅模式。
6. **事件目标**：通过 `EventTarget` 集中管理事件监听器。

具体每个类的详细用法请参考 [`architect.event.core`](event_core.md) 模块的文档。
