# 客户端属性 (Attr Client) API

`architect.attr.client` 模块提供了在客户端管理实体属性的机制，包括响应式属性、数据同步和持久化。

## `ReactiveAttrClient` 类

`ReactiveAttrClient` 是一个客户端属性的实现，它支持值变更的广播、与服务器同步以及本地持久化。

### 构造函数

#### `ReactiveAttrClient(entityId, name, defaultValue=None, broadcast=True, serverSync=False, persistent=False)`

- **`entityId`**: (字符串) 属性所属的实体 ID。
- **`name`**: (字符串) 属性的名称。
- **`defaultValue`**: (任意类型, 默认值 `None`) 属性的默认值。
- **`broadcast`**: (布尔值, 默认值 `True`) 属性值改变时是否广播 `ClientAttrEvents.AttrChange` 事件。
- **`serverSync`**: (布尔值, 默认值 `False`) 属性值改变时是否同步到服务器。
- **`persistent`**: (布尔值, 默认值 `False`) 属性是否进行本地持久化存储。

### 属性 (继承自 `ReactiveBase`)

- **`value`**: 属性的当前值。

### 内部方法 (不推荐直接调用)

虽然以下方法是内部方法，但理解它们有助于理解 `ReactiveAttrClient` 的行为：

- `_init()`: 初始化属性，包括加载、广播和同步。
- `_loadAttr()`: 如果 `persistent` 为 `True`，从本地数据库加载属性值。
- `_saveAttr()`: 如果 `persistent` 为 `True`，将属性值保存到本地数据库。
- `onDepEvent(evType)`: 依赖事件触发时的回调，处理属性的保存、广播和同步。
- `_sendServer()`: 如果 `serverSync` 为 `True`，向服务器发送属性同步事件。
- `_sync(value)`: 内部方法，用于从服务器同步属性值。
- `_broadcastAttr()`: 内部方法，用于广播属性变更事件。

## `attr` 类 (静态辅助类)

`attr` 类提供了一系列静态方法，用于创建不同配置的 `ReactiveAttrClient` 实例。

### 静态方法

#### `attr.mut(name, entity, defaultValue=None)`

创建一个可变属性。该属性不会同步到服务器，也不会进行持久化存储，但会广播事件。

- **`name`**: (字符串) 属性名称。
- **`entity`**: (字符串) 实体 ID。
- **`defaultValue`**: (任意类型, 默认值 `None`) 默认值。
- **返回值**: (`ReactiveAttrClient` 实例)

#### `attr.store(name, entity, defaultValue=None)`

创建一个可存储属性。该属性不会同步到服务器，也不会广播事件，但会进行本地持久化存储。

- **`name`**: (字符串) 属性名称。
- **`entity`**: (字符串) 实体 ID。
- **`defaultValue`**: (任意类型, 默认值 `None`) 默认值。
- **返回值**: (`ReactiveAttrClient` 实例)

#### `attr.remote(name, entity, defaultValue=None, persistent=False)`

创建一个远程属性。该属性不会广播事件，但会同步到服务器，并可选择是否持久化存储。

- **`name`**: (字符串) 属性名称。
- **`entity`**: (字符串) 实体 ID。
- **`defaultValue`**: (任意类型, 默认值 `None`) 默认值。
- **`persistent`**: (布尔值, 默认值 `False`) 是否进行本地持久化存储。
- **返回值**: (`ReactiveAttrClient` 实例)

#### `attr.shared(name, entity, defaultValue=None, persistent=False)`

创建一个共享属性。该属性会广播事件，同步到服务器，并可选择是否持久化存储。

- **`name`**: (字符串) 属性名称。
- **`entity`**: (字符串) 实体 ID。
- **`defaultValue`**: (任意类型, 默认值 `None`) 默认值。
- **`persistent`**: (布尔值, 默认值 `False`) 是否进行本地持久化存储。
- **返回值**: (`ReactiveAttrClient` 实例)

#### `attr.create(name, entity, defaultValue=None, broadcast=True, serverSync=False, persistent=False)`

通用属性创建方法。如果属性已存在，则返回现有实例。

- **`name`**: (字符串) 属性名称。
- **`entity`**: (字符串) 实体 ID。
- **`defaultValue`**: (任意类型, 默认值 `None`) 默认值。
- **`broadcast`**: (布尔值, 默认值 `True`) 是否广播事件。
- **`serverSync`**: (布尔值, 默认值 `False`) 是否同步到服务器。
- **`persistent`**: (布尔值, 默认值 `False`) 是否进行本地持久化存储。
- **返回值**: (`ReactiveAttrClient` 实例)

## `ModAttrClient` 类

`ModAttrClient` 是一个客户端子系统，负责接收来自服务器的属性同步事件，并更新本地 `ReactiveAttrClient` 实例。

### 静态属性

- **`attrs`**: (字典 `dict`) 存储所有 `(entityId, attrName)` 到 `ReactiveAttrClient` 实例的映射。

### 装饰器 (自动注册为客户端子系统)

`@SubsystemClient`

### 事件监听

#### `onServerSync(self, ev)`

监听 `ClientAttrEvents.ServerSync` 自定义事件，用于接收服务器发送的属性同步数据。

- **`ev`**: (字典 `dict`) 包含 `id` (实体 ID), `name` (属性名称) 和 `value` (属性值)。
