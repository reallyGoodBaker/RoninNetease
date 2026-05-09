# 服务端事件 (Event Server) API

`architect.event.server` 模块提供了服务端事件系统的实现，包括事件读取器和全局事件链管理。该模块与客户端事件模块 (`architect.event.client`) 结构相似，但针对服务端环境。

## `EventReader` 类

`EventReader` 是一个服务端组件，用于读取和处理事件链。

### 继承

- 继承自 `BaseCompServer`（服务端组件基类）。

### 构造函数

#### `onCreate(self, _)`

组件创建时初始化。

- **`_`**: (字符串) 实体 ID（未使用）。

### 属性

#### `ev`

- **类型**: `ChainedEvent` 或 `None`
- **说明**: 存储的事件对象。

### 方法

#### `event(self)`

获取当前存储的事件。

- **返回值**: (`ChainedEvent`) 事件对象。

### 注册

`EventReader` 被注册为服务端单例组件（非持久化）。

## `ServerEvents` 类

`ServerEvents` 是服务端全局事件管理器，负责创建和管理事件链。

### 静态属性

#### `globalEvents`

- **类型**: 字典 `dict`
- **说明**: 存储事件类型到 `EventChain` 实例的映射。

### 静态方法

#### `getOrCreateChain(eventType, isCustomEvent=False)`

获取或创建指定事件类型的事件链。

- **`eventType`**: (字符串) 事件类型名称。
- **`isCustomEvent`**: (布尔值, 默认值 `False`) 是否为自定义事件。
- **返回值**: (`EventChain`) 事件链实例。

#### 说明

- 如果事件类型已存在于 `globalEvents` 中，则返回现有的事件链。
- 否则，创建一个新的 `EventChain` 实例，并将其注册到子系统管理器 (`SubsystemManager`) 中，以便在事件触发时自动分发。

## `event(eventType, isCustomEvent=False)` 函数

便捷函数，用于获取或创建事件链。

- **`eventType`**: (字符串) 事件类型名称。
- **`isCustomEvent`**: (布尔值, 默认值 `False`) 是否为自定义事件。
- **返回值**: (`EventChain`) 事件链实例。

### 示例

```python
from ..architect.event.server import event

# 获取或创建事件链
player_join_chain = event('OnPlayerJoin', isCustomEvent=False)

# 添加事件监听器
@player_join_chain.listen
def on_player_join(ev):
    print('Player joined:', ev['player'])
```

## 使用示例

### 1. 使用 `EventReader` 组件

```python
from ..architect.component import getOrCreateSingletonComponent
from ..architect.event.server import EventReader

# 获取 EventReader 单例组件
reader = getOrCreateSingletonComponent(EventReader)

# 获取事件
chained_event = reader.event()
if chained_event:
    # 处理事件
    pass
```

### 2. 使用全局事件链

```python
from ..architect.event.server import event

# 定义自定义事件类型
MY_EVENT = 'my_custom_event'

# 获取事件链
my_event_chain = event(MY_EVENT, isCustomEvent=True)

# 添加监听器
@my_event_chain.listen
def on_my_event(ev):
    print('Custom event received:', ev)

# 在其他地方触发事件（通过子系统）
from ..subsystem import SubsystemManager
SubsystemManager.getInstance().broadcast(MY_EVENT, {'data': 'test'})
```

## 注意事项

1. **事件类型唯一性**: 每个事件类型对应一个全局的 `EventChain` 实例。
2. **自定义事件**: 如果事件是自定义事件（非引擎原生事件），需要设置 `isCustomEvent=True`。
3. **子系统集成**: 事件链会自动注册到子系统管理器，确保事件能够正确分发。
4. **单例组件**: `EventReader` 是单例组件，全局只有一个实例。
5. **服务端专用**: 该模块仅用于服务端环境，客户端应使用 `architect.event.client` 模块。

## 与客户端事件模块的差异

| 特性 | 服务端 (`architect.event.server`) | 客户端 (`architect.event.client`) |
|------|-----------------------------------|-----------------------------------|
| 组件基类 | `BaseCompServer` | `BaseCompClient` |
| 注册函数 | `_registerComponent(True, ...)` | `_registerComponent(False, ...)` |
| 子系统管理器 | 服务端子系统管理器 | 客户端子系统管理器 |
| 适用环境 | 服务端脚本 | 客户端脚本 |
