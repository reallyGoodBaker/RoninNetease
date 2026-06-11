# 组件系统 (ECS)

## 概念

RoninNetease 的 ECS 基于网易 SDK 的 `RegisterComponent`/`CreateComponent` 机制。框架额外提供了：

- **声明式组件定义** — `@Component` 装饰器
- **字段 Schema 与验证** — `@DefineFields` + `FieldSchema`
- **实体生命周期事件** — `Marker.onEntityCreated` / `onEntityDestroyed`
- **高效查询** — CompIndex 反向索引，`@Query` 自动注入

---

## 组件基类

```python
from architect.component import BaseCompServer, BaseCompClient

@Component()
class HealthComponent(BaseCompServer):

    def onCreate(self, entityId):
        "组件首次创建时调用。"
        self.value = 100

    def onDestroy(self, entityId):
        "组件被移除时调用。"
        pass

    def loadData(self, entityId):
        "仅持久化组件：从数据库加载后调用。"
        pass
```

---

## 字段 Schema — v1.1.0

`@DefineFields` 声明组件的期望字段、默认值和验证规则。框架在 `createComponent` 时自动初始化。

```python
from architect.component.schema import FieldSchema, DefineFields

@Component()
@DefineFields(
    health=FieldSchema(default=100, validator=lambda v: 0 <= v <= 1000),
    name=FieldSchema(default='unnamed'),
    tags=FieldSchema(default=[], validator=lambda v: isinstance(v, list) and len(v) <= 10),
)
class CharacterComponent(BaseCompServer):
    def onCreate(self, entityId):
        # 此时 health=100, name='unnamed', tags=[] 已自动设置
        self.level = 1
```

验证失败会抛出 `ValueError`：

```python
comp.health = 2000  # ValueError: Validation failed
```

---

## CRUD API

```python
from architect.component import createComponent, getOrCreateComponent, getOneComponent
from architect.component import hasComponent, destroyComponent, createSingletonComponent

# 创建（绑定到 entityId）
comp = createComponent(entityId, HealthComponent)

# 不存在则创建
comp = getOrCreateComponent(entityId, HealthComponent)

# 按实体验证是否拥有组件
if hasComponent(entityId, HealthComponent):
    comp = getOneComponent(entityId, HealthComponent)

# 单例组件（绑定到 levelId，全局唯一）
singleton = createSingletonComponent(GlobalDataComponent)

# 销毁
destroyComponent(entityId, HealthComponent)
```

---

## 实体生命周期事件 — v1.1.0

当实体首次获得组件或最后一个组件被移除时触发。

```python
from architect.component.core import _getEntityMarker

class CacheSystem(ServerSubsystem):

    def onInit(self):
        # 注册清理回调 — 实体销毁时自动清理缓存
        _getEntityMarker().onEntityDestroyed.on(self._on_entity_gone)
        self.cache = {}

    def _on_entity_gone(self, entityId):
        self.cache.pop(entityId, None)
```

---

## `@Query` — 自动遍历与注入

```python
from architect.compact import Sched, Query, EntityId

class HealthSystem(ServerSubsystem):

    @Sched.Tick()
    @Query(HealthComponent, EntityId)
    def tick_health(self, entityId, health):
        "框架自动：1) CompIndex 筛选实体 2) 注入 health/entityId 3) 调用此方法"
        if health.health <= 0:
            self.destroyEntity(entityId)
```

### required / excluded 过滤

```python
# 只处理同时拥有 Health 和 CombatAI 的实体
@Sched.Tick()
@Query(HealthComponent, required=[CombatAI])
def tick_combat(self, health):
    ...

# 排除已经标记为死亡的实体
@Sched.Tick()
@Query(HealthComponent, excluded=[DeadComponent])
def tick_alive(self, health):
    ...
```

### 额外参数注入

```python
from architect.compact import ExtraArguments, ExtraArgDict

@Sched.Tick()
@Query(HealthComponent, ExtraArguments, ExtraArgDict)
def process(self, health, args, kwargs):
    "args 和 kwargs 是外部传进来的位置/关键字参数元组/字典。"
```

---

## CompIndex 性能 — 为什么比全量遍历快

`CompIndex` 维护「组件名 → 持有该组件的实体 ID 集合」的反向索引。

```
@Query(RareComponent, HealthComponent)
→ sets = [{'e1', 'e3'}, {'e1', 'e2', 'e3', 'e5', 'e7'}]
→ 按集合大小升序 → [{'e1', 'e3'}, {50k entities}]
→ 交集: {'e1', 'e3'}  ← 只遍历 2 个实体
```

**最佳实践**: 查询中包含"稀有组件"作为第一个参数，让交集从最小的集合开始。

---

## 持久化组件

```python
from architect.component import PersistKeys

@Component(persist=True)
@PersistKeys('score', 'level', isGlobal=False)    # isGlobal=True → 跨存档全局数据库
class PlayerData(BaseCompServer):

    def onCreate(self, entityId):
        pass  # score/level 的 getter/setter 已被替换为 KV 数据库读写

    def loadData(self, entityId):
        print('Loaded:', self.score)
```

---

## 重要注意事项

- **始终通过框架 API 操作组件**（`createComponent`/`destroyComponent`）。直接调用网易 SDK 会导致 CompIndex 数据不一致
- **组件只存数据**，不放逻辑。逻辑应放在子系统类中
- `@Query` 必须配合 `@Sched.Tick()` 或 `@Sched.Render()` 使用
- `canTick` 必须为 `True` 才能驱动 `onUpdate` 及其中的 `@Query` 方法