# 组件系统

`architect` 的组件系统基于网易 SDK 的 `RegisterComponent` 机制封装，提供了声明式组件定义、生命周期管理和查询支持。

## 定义组件

使用 `@Component` 装饰器定义组件：

```python
from architect.component import Component, BaseCompServer, BaseCompClient

@Component(persist=False, singleton=False)
class MyComponent(BaseCompServer):
    def onCreate(self, entityId):
        # 组件创建时的初始化逻辑
        self.data = 0

    def onDestroy(self, entityId):
        # 组件销毁时的清理逻辑
        pass

    def loadData(self, entityId):
        # 如果 persist=True，在此处加载持久化数据
        pass
```

### 选项

- **`persist`**: (布尔值, 默认 False) 持久化组件。设置后可通过 `@PersistKeys` 声明需要持久化的键，框架自动处理序列化与反序列化。
- **`singleton`**: (布尔值, 默认 False) 单例组件。组件实例绑定在 LevelId 上，而非普通实体 ID。

### 组件基类

- **`BaseCompServer`**: 服务端组件基类，继承自 `serverApi.GetComponentCls()`
- **`BaseCompClient`**: 客户端组件基类，继承自 `clientApi.GetComponentCls()`

## 持久化键声明

使用 `@PersistKeys` 声明需要持久化的字段：

```python
from architect.component import PersistKeys

@Component(persist=True)
@PersistKeys('score', 'level', isGlobal=False)
class PlayerDataComponent(BaseCompServer):
    # score 和 level 会自动从数据库读写
    pass
```

- `isGlobal=True` 时使用客户端全局数据库 `ClientKVDatabaseGlobal`
- `isGlobal=False` 时使用客户端普通数据库 `ClientKVDatabase`

## 组件管理 API

```python
from architect.component.core import (
    createComponent,
    createComponents,
    createSingletonComponent,
    destroyComponent,
    getOneComponent,
    getOrCreateComponent,
    getComponent,
    getEntities,
    hasComponent,
    removeComponents,
    getOrCreateSingletonComponent,
)

# 创建组件
comp = createComponent(entityId, MyComponent)

# 批量创建
comps = createComponents(entityId, CompA, CompB)

# 创建单例组件
singleton = createSingletonComponent(MyComponent)

# 获取组件的第一个实例
comp = getOneComponent(entityId, MyComponent)

# 获取或创建
comp = getOrCreateComponent(entityId, MyComponent)

# 获取/创建单例
s = getOrCreateSingletonComponent(MyComponent)

# 获取多个组件（仅当实体拥有所有组件时才返回）
result = getComponent(entityId, [CompA, CompB])
# 返回 [CompA实例, CompB实例] 或 None

# 带查询条件的获取
comp = getComponentWithQuery(entityId, [CompA], required=[ReqComp], excluded=[ExcludeComp])

# 检查是否拥有所有指定组件
has = hasComponent(entityId, CompA, CompB)

# 销毁组件
destroyComponent(entityId, MyComponent)

# 批量销毁
removeComponents(entityId, CompA, CompB)

# 获取所有有组件标记的实体 ID
entities = getEntities()
```

## 组件内部标记

框架内部使用 `Marker` 类标记拥有组件的实体：

```python
from architect.component.core import entitiesServer, entitiesClient
```

- **`entitiesServer`**: 服务端标记集合
- **`entitiesClient`**: 客户端标记集合

## 引擎原生组件 (NeC / NeS)

`NeC`（客户端）和 `NeS`（服务端）提供了对引擎原生组件的便捷访问：

```python
from architect.component.common import NeS, NeC

# 获取引擎原生组件
attrComp = getOneComponent(playerId, NeS.Attr)
# 等价于 compServer.CreateAttr(playerId)

posComp = getOneComponent(entityId, NeC.Pos)
# 等价于 compClient.CreatePos(entityId)
```

通过前加 `#` 前缀的字符串名称也可获取原生组件：

```python
comp = getOneComponent(entityId, '#Attr')
```

## 查询系统 `@Query`

`@Query` 注解配合 `@Sched.Event` 或 `@Sched.Tick` 使用，自动筛选符合条件的实体并注入组件：

```python
from architect.query import Query, EntityId

# 筛选同时拥有 EntityId 和 MyComponent 的实体
@Sched.Tick()
@Query(EntityId, MyComponent)
def handle_logic(self, entityId, myComp):
    pass

# 增加 required / excluded 过滤
@Query(MyComponent, required=[RequiredComp], excluded=[ForbiddenComp])
def handle(self, myComp):
    pass
```

### 内置伪组件

- **`EntityId`**: 注入实体的 ID 字符串
- **`ExtraArguments`**: 注入调用方法时的位置参数列表
- **`ExtraArgDict`**: 注入调用方法时的关键字参数字典

## 查询缓存

`QueryServer` / `QueryClient` 提供缓存机制，提升频繁查询的性能：

```python
from architect.query.queryServer import QueryServer
from architect.query.queryClient import QueryClient

# 缓存的位置组件
pos = QueryServer.pos(entityId)

# 缓存的 Action 组件
action = QueryServer.action(entityId)
```

## 注册流程

组件注册在游戏启动时自动完成：