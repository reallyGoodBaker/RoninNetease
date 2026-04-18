# 事件系统 (Event)

`architect` 提供了便捷的事件监听方式，通过装饰器和统一的 API 管理引擎事件及自定义事件。

## @EventListener / @CustomEvent 装饰器

在子系统的方法上使用 `@EventListener` 装饰器，可以自动完成事件监听的注册与注销。

### 监听引擎事件
默认情况下，装饰器监听的是引擎的标准事件。
```python
@EventListener('PlayerJoinEvent')
def onPlayerJoin(self, ev):
    print(ev.playerId)
```

### 监听自定义事件
通过设置 `isCustomEvent=True` 监听自定义广播的事件。
```python
@EventListener('MyModEvent', isCustomEvent=True)
def onMyEvent(self, ev):
    pass
```

@CustomEvent 是 @EventListener 的别名，可以用于监听自定义事件。
与 @EventListener 不同的是，@CustomEvent 自带了 `isCustomEvent=True` 所以不需要手动设置。

## 编程式监听

除了装饰器，也可以在子系统中使用 `on` 和 `off` 方法：

```python
def onInit(self):
    self.on('SomeEvent', self.my_handler)

def my_handler(self, ev):
    pass

def onDestroy(self):
    # 装饰器会自动清理，但编程式监听建议手动清理（如果不是生命周期绑定的）
    self.off('SomeEvent', self.my_handler)
```

## 事件发送 (Broadcast)

- **广播事件**: `self.broadcast('EventName', {'data': 1})`
- **发送至客户端/服务端**: 参考 [Subsystem 模块](subsystem.md)。

## Tick
`Subsystem` 提供了 `onUpdate` 生命周期，每刻调用一次，若你需要使用 `Tick`, 请优先考虑使用 `onUpdate`。

```python
def onInit(self):
    # 设置 canTick 为 True，表示允许 onUpdate 被调用, 否则 onUpdate 不会被调用
    self.canTick = True

def onUpdate(self, dt):
    pass
```