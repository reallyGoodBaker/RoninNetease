# 组件系统 (ECS)

`architect` 的组件系统允许通过声明式的方式管理实体数据，并通过强大的查询机制实现数据驱动的逻辑。

## 定义组件

使用 `@Component` 装饰器定义组件：

```python
from ..architect.component import Component, BaseCompServer, BaseCompClient

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

- **persist**: (布尔值) 是否为持久化组件。
- **singleton**: (布尔值) 是否为单例组件（绑定在 LevelId 上）。

## 组件管理 API

框架提供了一系列 API 用于操作组件：

- `createComponent(entityId, cls)`: 为实体创建组件。
- `createComponents(entityId, *clsList)`: 批量创建组件。
- `createSingletonComponent(cls)`: 创建单例组件。
- `getOneComponent(entityId, cls)`: 获取实体的单个组件实例。
- `getOrCreateComponent(entityId, cls)`: 获取或在不存在时创建。
- `hasComponent(entityId, *clsList)`: 检查实体是否拥有指定的所有组件。
- `destroyComponent(entityId, cls)`: 销毁实体的指定组件。
- `removeComponents(entityId, *clsList)`: 批量销毁。
- `getEntities()`: 获取当前管理的所有实体 ID 列表。

## 引擎原生组件 (NeC & NeS)

通过 `NeC` (客户端) 和 `NeS` (服务端) 可以在 `architect` 中像操作自定义组件一样操作引擎原生组件。

```python
from ..architect.component import NeS

# 获取玩家的等级组件 (原生)
lvComp = getOneComponent(playerId, NeS.Lv)
# 相当于 compServer.CreateLv(playerId)
```

## @Query 查询系统

`@Query` 是 ECS 的核心，用于在调度任务中自动筛选符合条件的实体并注入组件实例。

### 基本用法
```python
from ..architect.query import Query, EntityId

@Sched.Tick()
@Query(EntityId, MyComponent, NeS.Attr)
def handle_logic(self, entityId, myComp, attrComp):
    # 框架会自动遍历所有同时拥有 MyComponent 和 Attr 的实体
    pass
```

### 伪组件 (Pseudo-components)
- **EntityId**: 注入实体的 ID。
- **ExtraArguments**: 注入调用方法时的位置参数列表。
- **ExtraArgDict**: 注入调用方法时的关键字参数字典。

### 查询选项
```python
@Query(MyComponent, required=[RequiredComp], excluded=[ForbiddenComp])
def handle(self, myComp):
    # 仅查询拥有 MyComponent 且 拥有 RequiredComp 且 没有 ForbiddenComp 的实体
    pass
```

## 查询缓存与静态访问

- **QueryServer / QueryClient**: 提供了一些静态方法快速获取常用引擎组件的缓存实例（如 `pos(id)`, `action(id)`, `dimension(id)` 等）。
