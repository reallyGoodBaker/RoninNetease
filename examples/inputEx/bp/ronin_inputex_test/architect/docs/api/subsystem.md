# Subsystem API

`architect.subsystem` 模块是框架的核心，定义了模组逻辑的组织方式、生命周期管理以及客户端/服务端之间的通信机制。

## `EventListener` 类 (内部工具)

这是一个内部类，用于封装事件监听器。通常通过 `@EventListener` 装饰器或 `Subsystem.on()/listen()` 方法间接使用。

### 构造函数

#### `EventListener(evType, fn)`

- **`evType`**: (字符串) 事件类型。
- **`fn`**: (函数 `FunctionType`) 事件处理器函数。

## `SubsystemManager` 类 (内部工具)

这是一个内部管理类，负责注册、创建和管理所有的子系统实例。开发者通常无需直接与之交互。

### 静态方法

#### `SubsystemManager.getInstance()`

获取当前线程的 `SubsystemManager` 实例（客户端或服务端）。

- **返回值**: (`SubsystemManager` 实例)

#### `SubsystemManager.createClient(engine, sysName, clientDir=None)`

创建客户端的 `SubsystemManager` 实例并注册系统。通常在 `modMain.py` 中调用。

- **`engine`**: (字符串) 引擎命名空间。
- **`sysName`**: (字符串) 系统名称。
- **`clientDir`**: (字符串, 可选) 客户端子系统的模块路径。
- **返回值**: (`SubsystemManager` 实例)

#### `SubsystemManager.createServer(engine, sysName, serverDir=None)`

创建服务端的 `SubsystemManager` 实例并注册系统。通常在 `modMain.py` 中调用。

- **`engine`**: (字符串) 引擎命名空间。
- **`sysName`**: (字符串) 系统名称。
- **`serverDir`**: (字符串, 可选) 服务端子系统的模块路径。
- **返回值**: (`SubsystemManager` 实例)

#### `SubsystemManager.registerSubsystem(subsystemCls)`

注册一个子系统类，使其在 `SubsystemManager` 初始化时自动创建实例。通常通过 `@SubsystemClient` 或 `@SubsystemServer` 装饰器间接调用。

- **`subsystemCls`**: (类 `class`) 要注册的子系统类。

#### `SubsystemManager.unregisterSubsystems()`

清空所有已注册的子系统类列表。

## `subsystem` 类 (静态辅助类)

这是一个静态工具类，提供了一些便捷的静态方法，用于在不直接持有子系统实例的情况下执行常用操作。它通过内部寻找第一个注册的子系统来代理调用。

### 静态方法

#### `subsystem.sendServer(event, data)`

(仅限客户端调用) 向服务端发送一个事件和数据。

- **`event`**: (字符串) 事件名称。
- **`data`**: (字典 `dict`) 要发送的数据。

#### `subsystem.sendClient(target, event, data)`

(仅限服务端调用) 向指定的客户端发送一个事件和数据。

- **`target`**: (字符串/整数/列表) 目标客户端的玩家 ID 或 ID 列表。
- **`event`**: (字符串) 事件名称。
- **`data`**: (字典 `dict`) 要发送的数据。

#### `subsystem.sendAllClients(event, data)`

(仅限服务端调用) 向所有客户端发送一个事件和数据。

- **`event`**: (字符串) 事件名称。
- **`data`**: (字典 `dict`) 要发送的数据。

#### `subsystem.spawnServerEntity(template, location, rot, isNpc=False, isGlobal=False)`

(仅限服务端调用) 在服务端生成一个实体。

- **`template`**: (字符串或字典 `dict`) 实体模板（如 `"minecraft:zombie"`）或 NBT 字典。
- **`location`**: (`Location` 对象) 实体的生成位置和维度。
- **`rot`**: (元组 `tuple[float, float]`) 实体的 Y 轴和 X 轴旋转角度。
- **`isNpc`**: (布尔值 `bool`, 默认值 `False`) 是否为 NPC 实体。
- **`isGlobal`**: (布尔值 `bool`, 默认值 `False`) 是否为全局实体。
- **返回值**: (字符串) 生成实体的 ID，如果失败则为 `None`。

#### `subsystem.spawnClientEntity(template, pos, rot)`

(仅限客户端调用) 在客户端生成一个实体。

- **`template`**: (字符串或字典 `dict`) 实体模板或 NBT 字典。
- **`pos`**: (元组 `tuple[float, float, float]`) 实体的三维坐标。
- **`rot`**: (元组 `tuple[float, float]`) 实体的 Y 轴和 X 轴旋转角度。
- **返回值**: (字符串) 生成实体的 ID，如果失败则为 `None`。

#### `subsystem.spawnItem(itemCls, *args, **kwargs)`

(仅限服务端调用) 生成一个物品实体。

- **`itemCls`**: (物品类或字典) 物品的类或物品 NBT 字典。
- **`*args`, `**kwargs`**: 传递给底层物品创建方法的额外参数。
- **返回值**: 生成的物品实体 ID。

#### `subsystem.addListener(event, fn, isCustomEvent=False)`

(不推荐直接使用) 监听一个事件。建议使用 `Subsystem` 实例的 `on()/listen()` 方法。

#### `subsystem.removeListener(event, fn, isCustomEvent=False)`

(不推荐直接使用) 移除一个事件监听器。建议使用 `Subsystem` 实例的 `off()/unlisten()` 方法。

## 子系统注册装饰器

#### `SubsystemClient(subsystemCls)`

装饰器，用于将一个类标记为客户端子系统，并在客户端初始化时自动注册。

- **`subsystemCls`**: (类 `class`) 客户端子系统类。
- **返回值**: 原始的子系统类。

#### `SubsystemServer(subsystemCls)`

装饰器，用于将一个类标记为服务端子系统，并在服务端初始化时自动注册。

- **`subsystemCls`**: (类 `class`) 服务端子系统类。
- **返回值**: 原始的子系统类。

## 全局函数

#### `getSubsystemCls()`

获取当前运行环境（客户端或服务端）的子系统基类（`ServerSubsystem` 或 `ClientSubsystem`）。

- **返回值**: (类 `class`) `ServerSubsystem` 或 `ClientSubsystem`。

#### `createServer(engine, sysName, serverDir=None)`

在 `modMain.py` 中调用的便捷函数，用于创建和初始化服务端 `SubsystemManager`。

- **`engine`**: (字符串) 引擎命名空间。
- **`sysName`**: (字符串) 系统名称。
- **`serverDir`**: (字符串, 可选) 服务端子系统的模块路径。
- **返回值**: (`SubsystemManager` 实例)

#### `createClient(engine, sysName, clientDir=None)`

在 `modMain.py` 中调用的便捷函数，用于创建和初始化客户端 `SubsystemManager`。

- **`engine`**: (字符串) 引擎命名空间。
- **`sysName`**: (字符串) 系统名称。
- **`clientDir`**: (字符串, 可选) 客户端子系统的模块路径。
- **返回值**: (`SubsystemManager` 实例)

## `Subsystem` 基类

所有客户端和服务端子系统的基类，定义了子系统的核心行为和生命周期。

### 构造函数

#### `Subsystem(system, engine, sysName)`

- **`system`**: (对象 `object`) 底层引擎系统实例。
- **`engine`**: (字符串) 引擎命名空间。
- **`sysName`**: (字符串) 系统名称。

### 属性

- **`system`**: 底层引擎系统实例。
- **`engine`**: 引擎命名空间。
- **`sysName`**: 系统名称。
- **`ticks`**: (整数) 当前子系统被更新的次数。
- **`canTick`**: (布尔值) 是否允许 `onUpdate` 方法被调用。默认 `False`。
- **`initialized`**: (布尔值) 子系统是否已完成初始化。

### 生命周期方法

#### `onUpdate(self, dt)`

每 Tick 调用一次，前提是 `self.canTick` 为 `True`。

- **`dt`**: (浮点数 `float`) 自上次调用以来的时间差。

#### `onReady(self)`

所有子系统初始化完毕后调用。此时可以安全地通过 `getSubsystem` 获取其他子系统。

#### `onInit(self)`

当前子系统实例创建完毕后调用。此时 `SubystemManager` 已创建，但其他子系统可能尚未完全就绪。

#### `onDestroy(self)`

子系统销毁时调用，用于执行清理工作。

### 实例方法

#### `getSubsystem(cls)`

获取指定类的子系统实例。

- **`cls`**: (类 `class`) 目标子系统类。
- **返回值**: (`Subsystem` 实例) 指定类的子系统实例。

#### `getSubsystemByName(name)`

通过名称获取子系统实例。

- **`name`**: (字符串) 目标子系统类的名称。
- **返回值**: (`Subsystem` 实例) 指定名称的子系统实例。

#### `removeSubsystem(subsystemCls)`

移除指定类的子系统实例。

- **`subsystemCls`**: (类 `class`) 要移除的子系统类。

#### `getInstance()`

获取当前子系统类的单例实例。

- **返回值**: (`Subsystem` 实例)

#### `getHost()`

获取底层的引擎系统实例。

- **返回值**: (`_ShadowSystemServer` 或 `_ShadowSystemClient` 实例)

#### `getEngine()`

获取引擎命名空间。

- **返回值**: (字符串)

#### `getSysName()`

获取系统名称。

- **返回值**: (字符串)

#### `on(eventName, handler, isCustomEvent=True)`

监听自定义事件。

- **`eventName`**: (字符串) 事件名称。
- **`handler`**: (函数 `FunctionType`) 事件处理器函数。
- **`isCustomEvent`**: (布尔值, 默认值 `True`) 是否为自定义事件。
- **返回值**: (字符串) 事件监听器的唯一标识。

#### `off(eventName, handler, isCustomEvent=True)`

移除自定义事件监听器。

- **`eventName`**: (字符串) 事件名称。
- **`handler`**: (函数 `FunctionType`) 事件处理器函数。
- **`isCustomEvent`**: (布尔值, 默认值 `True`) 是否为自定义事件。
- **返回值**: (字符串) 事件监听器的唯一标识。

#### `listen(eventName, handler)`

监听引擎原生事件（非自定义事件）。

- **`eventName`**: (字符串) 事件名称。
- **`handler`**: (函数 `FunctionType`) 事件处理器函数。
- **返回值**: (字符串) 事件监听器的唯一标识。

#### `unlisten(eventName, handler)`

移除引擎原生事件监听器。

- **`eventName`**: (字符串) 事件名称。
- **`handler`**: (函数 `FunctionType`) 事件处理器函数。
- **返回值**: (字符串) 事件监听器的唯一标识。

#### `broadcast(eventName, eventData)`

广播自定义事件。

- **`eventName`**: (字符串) 事件名称。
- **`eventData`**: (字典 `dict`) 要广播的事件数据。
- **返回值**: (字符串) 事件 ID。

#### `scheduleFixed(schedName, period=1)`

添加一个固定频率的调度器。注意：不要在 `onInit` 中调用，因为游戏此时可能尚未完全初始化。

- **`schedName`**: (字符串) 调度器的名称。
- **`period`**: (整数/浮点数, 默认值 `1`) 调度周期（秒）。
- **返回值**: (`SimpleFixedScheduler` 实例)

#### `stopFixed(schedName)`

停止并移除一个固定频率调度器。

- **`schedName`**: (字符串) 调度器的名称。
- **返回值**: (布尔值 `bool`) 如果成功停止则返回 `True`，否则返回 `False`。

## `ServerSubsystem` 类

服务端子系统的基类，继承自 `Subsystem`，并添加了服务端特有的通信和实体操作方法。

### 构造函数

#### `ServerSubsystem(system, engine, sysName)`

- **`system`**: (对象 `object`) 底层引擎系统实例。
- **`engine`**: (字符串) 引擎命名空间。
- **`sysName`**: (字符串) 系统名称。

### 方法

#### `sendAllClients(eventName, eventData)`

向所有客户端广播事件。

- **`eventName`**: (字符串) 事件名称。
- **`eventData`**: (字典 `dict`) 事件数据。

#### `sendClient(targetIds, eventName, eventData)`

向一个或多个客户端发送事件。

- **`targetIds`**: (字符串/整数/列表) 目标客户端的玩家 ID 或 ID 列表。
- **`eventName`**: (字符串) 事件名称。
- **`eventData`**: (字典 `dict`) 事件数据。

#### `spawnEntity(template, location, rot, isNpc=False, isGlobal=False)`

在服务端生成一个实体。支持通过模板字符串或 NBT 字典创建。

- **`template`**: (字符串或字典 `dict`) 实体模板或 NBT 字典。
- **`location`**: (`Location` 对象) 实体的生成位置和维度。
- **`rot`**: (元组 `tuple[float, float]`) 旋转角度。
- **`isNpc`**: (布尔值, 默认值 `False`) 是否为 NPC。
- **`isGlobal`**: (布尔值, 默认值 `False`) 是否为全局实体。
- **返回值**: 生成实体的 ID，如果失败则为 `None`。

#### `destroyEntity(entityId)`

销毁服务端实体。

- **`entityId`**: (字符串) 要销毁的实体 ID。
- **返回值**: (布尔值 `bool`) 是否成功销毁。

#### `spawnItem(itemDict, location)`

在指定位置生成一个物品实体。

- **`itemDict`**: (字典 `dict`) 物品的 NBT 数据。
- **`location`**: (`Location` 对象) 物品的生成位置和维度。
- **返回值**: 生成的物品实体 ID。

## `ClientSubsystem` 类

客户端子系统的基类，继承自 `Subsystem`，并添加了客户端特有的通信和实体操作方法。

### 构造函数

#### `ClientSubsystem(system, engine, sysName)`

- **`system`**: (对象 `object`) 底层引擎系统实例。
- **`engine`**: (字符串) 引擎命名空间。
- **`sysName`**: (字符串) 系统名称。

### 方法

#### `sendServer(eventName, eventData)`

向服务端发送事件。

- **`eventName`**: (字符串) 事件名称。
- **`eventData`**: (字典 `dict`) 事件数据。

#### `spawnEntity(typeStr, pos, rot)`

在客户端生成一个实体。

- **`typeStr`**: (字符串) 实体类型字符串。
- **`pos`**: (元组 `tuple[float, float, float]`) 实体的三维坐标。
- **`rot`**: (元组 `tuple[float, float]`) 旋转角度。
- **返回值**: 生成实体的 ID，如果失败则为 `None`。

#### `onRender(self, dt)`

每渲染帧调用。此处可以放置与渲染相关的逻辑。

- **`dt`**: (浮点数 `float`) 自上次调用以来的时间差。

#### `destroyEntity(entityId)`

销毁客户端实体。

- **`entityId`**: (字符串) 要销毁的客户端实体 ID。

#### `createSfx(path, pos=None, rot=None, scale=None)`

创建引擎特效 (SFX)。

- **`path`**: (字符串) 特效资源路径。
- **`pos`**: (元组 `tuple[float, float, float]`, 可选) 位置。
- **`rot`**: (元组 `tuple[float, float]`, 可选) 旋转。
- **`scale`**: (浮点数 `float`, 可选) 缩放。
- **返回值**: 特效实体 ID。

#### `createParticle(path, pos)`

创建引擎粒子效果。

- **`path`**: (字符串) 粒子资源路径。
- **`pos`**: (元组 `tuple[float, float, float]`) 位置。
- **返回值**: 粒子实体 ID。

#### `createEffectBind(path, bindEntity, aniName)`

创建绑定到实体的效果。

- **`path`**: (字符串) 效果资源路径。
- **`bindEntity`**: (字符串) 绑定实体 ID。
- **`aniName`**: (字符串) 动画名称。
- **返回值**: 效果实体 ID。

#### `destroySfx(entityId)`

销毁引擎特效。

- **`entityId`**: (字符串) 要销毁的特效实体 ID。
