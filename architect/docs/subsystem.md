# 子系统 (Subsystem)

子系统是 `architect` 框架中承载业务逻辑的基础单元。它通过装饰器实现自动注册，并管理自身的生命周期。

## 注册子系统

- **@SubsystemServer**: 仅在服务端注册。
- **@SubsystemClient**: 仅在客户端注册。

```python
from ..architect.subsystem import ServerSubsystem, SubsystemServer, SubsystemClient, ClientSubsystem

@SubsystemServer
class MyServerService(ServerSubsystem):
    pass

@SubsystemClient
class MyClientService(ClientSubsystem):
    pass
```

## 生命周期方法

子系统提供了一系列生命周期回调，方便在不同阶段初始化逻辑：

| 方法 | 说明 |
| --- | --- |
| `onInit(self)` | 子系统实例创建完成，但其他子系统可能尚未全部创建。在此处通常进行内部状态初始化和事件绑定。 |
| `onReady(self)` | 所有子系统均已创建并初始化完成。此时可以使用 `self.getSubsystem(Cls)` 安全地获取其他子系统。 |
| `onUpdate(self, dt)` | 每 tick 调用。需设置 `self.canTick = True` 才会生效。 |
| `onRender(self, dt)` | 每渲染帧调用（仅限客户端子系统）。 |
| `onDestroy(self)` | 子系统销毁时调用，用于清理资源、注销事件监听等。 |

## 核心实例方法

- `self.getHost()`: 获取底层的引擎系统实例。
- `self.getEngine()`: 获取引擎命名空间。
- `self.getSysName()`: 获取引擎系统名称。
- `self.broadcast(eventName, eventData)`: 广播自定义事件。
- `self.sendServer(eventName, eventData)`: (仅限客户端) 向服务端发送通知。
- `self.sendClient(targetIds, eventName, eventData)`: (仅限服务端) 向指定客户端发送通知。`targetIds` 可以是字符串、整数或列表。
- `self.sendAllClients(eventName, eventData)`: (仅限服务端) 向所有客户端发送广播。
- `self.spawnEntity(template, location, rot, isNpc=False, isGlobal=False)`: 生成实体。`template` 支持类型字符串或 NBT 字典。
- `self.destroyEntity(entityId)`: 销毁实体。
- `self.spawnItem(itemDict, location)`: (仅限服务端) 在指定位置生成物品。

## 全局静态方法 (subsystem 类)

`architect.subsystem.subsystem` 提供了一些静态方法，允许在不持有子系统实例的情况下执行常用操作（通过自动寻找第一个注册的子系统实现）：

```python
from ..architect.subsystem import subsystem

subsystem.sendServer('Event', {})
subsystem.sendClient(playerId, 'Event', {})
subsystem.spawnServerEntity('minecraft:zombie', location, (0, 0))
subsystem.addListener('Event', handler)
```

## 基础工具 API

- `architect.basic.isServer()`: 判断当前是否运行在服务端。
- `architect.basic.compServer` / `compClient`: 直接访问引擎组件工厂。
- `architect.basic.serverTick()`: 获取服务端 tick 时间。
- `architect.basic.Location(pos, dim)`: 封装坐标与维度的位置对象。
