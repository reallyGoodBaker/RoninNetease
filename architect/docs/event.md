# 事件系统 (Event)

`architect` 提供了便捷的事件监听方式，通过装饰器和统一的 API 管理引擎事件及自定义事件。

## @EventListener 装饰器

在子系统的方法上使用 `@EventListener` 装饰器，可以自动完成事件监听的注册与注销。

### 监听引擎事件
默认情况下，装饰器监听的是引擎的标准事件。
```python
@EventListener('PlayerJoinEvent')
def onPlayerJoin(self, ev):
    # ev 为事件参数字典
    print(ev['playerId'])
```

### 监听自定义事件
通过设置 `isCustomEvent=True` 监听自定义广播的事件。
```python
@EventListener('MyModEvent', isCustomEvent=True)
def onMyEvent(self, ev):
    pass
```

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
