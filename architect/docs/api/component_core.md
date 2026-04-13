# 组件核心 (Component Core) API

`architect.component.core` 模块是组件系统的核心实现，提供了组件的注册、创建、查询、销毁等基础功能。

## 全局变量

- **`clientCompCls`**: (列表) 存储客户端组件类。
- **`serverCompCls`**: (列表) 存储服务端组件类。
- **`components`**: (字典) 存储已创建的组件实例，键为 `(entityId, componentKey)`。
- **`entitiesServer`**: (字典) 服务端实体计数器。
- **`entitiesClient`**: (字典) 客户端实体计数器。

## 辅助函数

### `singletonId()`

获取单例组件的实体 ID（即当前关卡 ID）。

- **返回值**: (字符串) 服务端返回 `serverApi.GetLevelId()`，客户端返回 `clientApi.GetLevelId()`。

### `_registerComponent(isServer, cls, persist=False, singleton=False)`

内部函数，注册组件类。

- **`isServer`**: (布尔值) 是否为服务端组件。
- **`cls`**: (类) 组件类。
- **`persist`**: (布尔值, 默认值 `False`) 是否为持久化组件。
- **`singleton`**: (布尔值, 默认值 `False`) 是否为单例组件。

### `_registerCompsIntoGame(isHost)`

内部函数，将组件注册到游戏引擎。

- **`isHost`**: (布尔值) 是否为服务端。

### `getComponentAnnotation(cls)`

获取组件的注解信息。

- **`cls`**: (类) 组件类。
- **返回值**: (字典) 组件的注解信息，包含 `persist` 和 `singleton` 字段。

### `isPersistComponent(cls)`

判断组件是否为持久化组件。

- **`cls`**: (类) 组件类。
- **返回值**: (布尔值) 是否为持久化组件。

## 组件装饰器

### `Component(persist=False, singleton=False)`

组件装饰器，用于标记一个类为组件。

- **`persist`**: (布尔值, 默认值 `False`) 是否为持久化组件。
- **`singleton`**: (布尔值, 默认值 `False`) 是否为单例组件。

#### 示例

```python
from ..architect.component import Component

@Component(persist=True, singleton=False)
class MyComponent:
    def __init__(self):
        self.data = 0
```

## 组件操作函数

### `createComponent(entityId, cls)`

创建组件实例。

- **`entityId`**: (字符串) 实体 ID。
- **`cls`**: (类或字符串) 组件类或组件名称。
- **返回值**: (组件实例) 创建的组件实例。

### `createSingletonComponent(cls)`

创建单例组件实例。

- **`cls`**: (类) 组件类。
- **返回值**: (组件实例) 创建的组件实例。

### `createComponents(entityId, *clsList)`

批量创建组件。

- **`entityId`**: (字符串) 实体 ID。
- **`*clsList`**: (可变参数) 组件类列表。
- **返回值**: (列表) 创建的组件实例列表。

### `destroyComponent(entityId, cls)`

销毁组件实例。

- **`entityId`**: (字符串) 实体 ID。
- **`cls`**: (类或字符串) 组件类或组件名称。
- **返回值**: (布尔值) 是否成功销毁。

### `getOneComponent(entityId, cls)`

获取单个组件实例。

- **`entityId`**: (字符串) 实体 ID。
- **`cls`**: (类或字符串) 组件类或组件名称。
- **返回值**: (组件实例) 组件实例，如果不存在则返回 `None`。

### `getOneSingletonComponent(cls)`

获取单例组件实例。

- **`cls`**: (类) 组件类。
- **返回值**: (组件实例) 组件实例，如果不存在则返回 `None`。

### `getComponent(entityId, clsList)`

获取多个组件实例。

- **`entityId`**: (字符串) 实体 ID。
- **`clsList`**: (列表) 组件类或组件名称列表。
- **返回值**: (列表) 组件实例列表，如果任一组件不存在则返回 `None`。

### `getComponentWithQuery(entityId, targets, required=[], excluded=[])`

根据查询条件获取组件实例。

- **`entityId`**: (字符串) 实体 ID。
- **`targets`**: (列表) 目标组件列表。
- **`required`**: (列表, 默认值 `[]`) 必须存在的组件列表。
- **`excluded`**: (列表, 默认值 `[]`) 必须不存在的组件列表。
- **返回值**: (列表) 组件实例列表，如果条件不满足则返回 `None`。

### `getOrCreateComponent(entityId, cls)`

获取或创建组件实例。

- **`entityId`**: (字符串) 实体 ID。
- **`cls`**: (类或字符串) 组件类或组件名称。
- **返回值**: (组件实例) 组件实例。

### `getOrCreateSingletonComponent(cls)`

获取或创建单例组件实例。

- **`cls`**: (类) 组件类。
- **返回值**: (组件实例) 组件实例。

### `getEntities()`

获取所有拥有组件的实体 ID 列表。

- **返回值**: (列表) 实体 ID 列表。

### `hasComponent(entityId, *desc)`

检查实体是否拥有指定的组件。

- **`entityId`**: (字符串) 实体 ID。
- **`*desc`**: (可变参数) 组件类或组件名称列表。
- **返回值**: (布尔值) 是否拥有所有指定的组件。

### `removeComponents(entityId, *clsList)`

批量移除组件。

- **`entityId`**: (字符串) 实体 ID。
- **`*clsList`**: (可变参数) 组件类或组件名称列表。

## 基础组件类

### `BaseCompServer` 类

服务端组件基类，继承自 `serverApi.GetComponentCls()`。

#### 方法

- `onCreate(self, entityId)`: 组件创建时调用。
- `onDestroy(self, entityId)`: 组件销毁时调用。
- `loadData(self, entityId)`: 组件加载数据时调用。

### `BaseCompClient` 类

客户端组件基类，继承自 `clientApi.GetComponentCls()`。

#### 方法

- `onCreate(self, entityId)`: 组件创建时调用。
- `onDestroy(self, entityId)`: 组件销毁时调用。
- `loadData(self, entityId)`: 组件加载数据时调用。

## 使用示例

```python
from ..architect.component import Component, createComponent, getComponent, destroyComponent

# 定义组件
@Component(persist=True)
class HealthComponent:
    def __init__(self):
        self.health = 100

# 创建组件
entity_id = "player_123"
health_comp = createComponent(entity_id, HealthComponent)

# 获取组件
health_comp = getComponent(entity_id, [HealthComponent])[0]

# 销毁组件
destroyComponent(entity_id, HealthComponent)
```
