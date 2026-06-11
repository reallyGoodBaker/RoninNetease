# ECS — 实体组件系统

RoninNetease 实现了基于 CompIndex（组件反向索引）的 ECS 架构，将实体的数据和逻辑分离到可组合的组件中。

---

## 1. 核心概念

| 概念 | 说明 |
|---|---|
| **Entity** | 由引擎管理的游戏对象（实体 ID 为 `str`） |
| **Component** | 附着在实体上的纯数据容器，无逻辑 |
| **CompIndex** | 反向索引：每种组件类型维护 `{entityId: instance}` 字典 |
| **System** | 继承自 `Subsystem` 的逻辑处理单元，通过 `@Query` 遍历实体 |

---

## 2. 定义组件

### 2.1 基本组件

```python
from architect.component import Component

class Health(Component):
    hp = 100
    maxHp = 100

class Transform(Component):
    x = 0.0
    y = 0.0
    z = 0.0
    yaw = 0.0
    pitch = 0.0
```

`Component` 是所有自定义组件的基类。类属性会作为实例的默认值。

### 2.2 持久化组件 — `@PersistKeys`

`@PersistKeys` 是一个**类装饰器**，接收需要持久化的字段名作为参数：

```python
from architect.component import Component, PersistKeys

@PersistKeys('slots', 'selected')
class Inventory(Component):
    slots = [''] * 36
    selected = 0
```

标记后，这些字段的值会在实体卸载/重载时自动保存和恢复。

### 2.3 带字段验证的组件 — `@DefineFields`

```python
from architect.component.schema import DefineFields, FieldSchema

@DefineFields({
    'level': FieldSchema(default=1,
                         validator=lambda v: v >= 1),
    'xp': FieldSchema(default=0,
                      validator=lambda v: v >= 0),
    'health': FieldSchema(default=100.0,
                          validator=lambda v: 0.0 <= v <= 1000.0),
    'name': FieldSchema(default='Unknown')
})
class PlayerStats(Component):
    pass
```

`FieldSchema(default, validator)` 参数：
- `default` — 字段的默认值
- `validator` — 可选的验证函数，接收值返回 `bool`。验证失败时会打印警告。

`@DefineFields` 声明的字段会在 `createComponent()` 时自动初始化到组件实例。

---

## 3. 创建、获取与销毁组件

### 3.1 API 速查

| 函数 | 签名 | 说明 |
|---|---|---|
| `createComponent` | `(entityId: str, cls: type) -> instance` | 创建并附着组件 |
| `getOrCreateComponent` | `(entityId: str, cls: type) -> instance` | 获取已有或创建新组件 |
| `getComponent` | `(entityId: str, cls: type) -> instance \| None` | 获取组件，不存在返回 None |
| `hasComponent` | `(entityId: str, cls: type) -> bool` | 检查组件存在性 |
| `destroyComponent` | `(entityId: str, cls: type) -> None` | 销毁组件 |
| `removeComponents` | `(entityId: str) -> None` | 移除实体上的所有组件 |
| `getEntities` | `(cls: type) -> set[str]` | 获取所有拥有该组件的实体 ID 集 |
| `isPersistComponent` | `(cls: type) -> bool` | 检查组件是否声明了持久化 |

### 3.2 示例

```python
from architect.component import (
    createComponent, getOrCreateComponent, getComponent,
    hasComponent, destroyComponent, getEntities
)

# 创建
health = createComponent('entity_abc', Health)

# 获取或创建
health = getOrCreateComponent('entity_abc', Health)
health.hp = max(0, health.hp - 10)

# 检查
if not hasComponent('entity_abc', Armor):
    createComponent('entity_abc', Armor)

# 查询所有拥有 Health 组件的实体
all_entities = getEntities(Health)  # {'entity_abc', 'entity_xyz', ...}

# 销毁
destroyComponent('entity_abc', Health)
```

### 3.3 单例组件

某些组件每个实体只应该有一个实例（如 `EventReader`），框架提供了单例风格的 API：

```python
from architect.component import (
    getOrCreateSingletonComponent,
    destroySingletonComponent
)

# 获取或创建
reader = getOrCreateSingletonComponent('EventReader')

# 销毁
destroySingletonComponent('EventReader')
```

---

## 4. 查询实体 — `@Query`

### 4.1 基本用法

`@Query` 接收组件类作为位置参数，按顺序注入到方法参数中。用 `EntityId` 伪组件获取实体 ID：

```python
from architect.query import Query, EntityId

class DamageSystem(ServerSubsystem):
    canTick = True

    @Query(Health, Transform, EntityId,
           required=[PlayerStats],
           excluded=[Dead])
    def process(self, health, transform, entityId):
        # health: Health 实例
        # transform: Transform 实例
        # entityId: 实体 ID (str)
        # 注：required 中的 PlayerStats 仅用于筛选，不注入到参数
        health.hp -= 1

    def onUpdate(self, dt):
        self.process()  # 遍历所有匹配实体
```

### 4.2 `@Query` 参数详解

```python
def Query(*compCls, **options):
```

| 参数 | 类型 | 说明 |
|---|---|---|
| `*compCls` | 位置参数 | 组件类型列表，按顺序注入到被装饰方法的参数中 |
| `required` | `list` | 必须额外存在的组件（不注入到参数中） |
| `excluded` | `list` | 必须排除的组件 |

### 4.3 伪组件

| 伪组件 | 注入值 |
|---|---|
| `EntityId` | 实体 ID 字符串 |
| `ExtraArguments` | 调用 wrapper 时传入的 `*args` |
| `ExtraArgDict` | 调用 wrapper 时传入的 `**kwargs` |

伪组件可以放在参数列表的任意位置，框架自动替换对应的值。

### 4.4 查询装饰器内部机制

`@Query` 装饰器修改被装饰方法的行为：
- 不带参数调用时 → 遍历所有匹配实体，注入参数后逐次调用
- 带参数调用时 → 传入的参数作为 `*args` 和 `**kwargs`（可通过 `ExtraArguments`/`ExtraArgDict` 获取）

```python
# 处理所有匹配实体
self.process()

# 带额外参数（需要 ExtraArgDict 伪组件接收）
self.process(some_flag=True)
```

---

## 5. CompIndex 缓存

框架维护组件类型的反向索引。当组件被创建或销毁时，索引自动更新：

```
CompIndex
├── Health   → {'e1': <Health hp=90>, 'e2': <Health hp=50>, 'e3': <Health hp=80>}
├── Transform → {'e1': <Transform ...>, 'e2': <Transform ...>}
├── PlayerStats → {'e1': <PlayerStats level=3>, 'e3': <PlayerStats level=1>}
└── ...
```

查询 `(Health, Transform, EntityId)` 时：
1. 取 `Health` 实体集 ∩ `Transform` 实体集
2. 遍历结果，注入对应组件实例

---

## 6. Marker — 实体标记组件

`Marker` 是一个特殊的生命周期标记组件，用于追踪实体的创建和销毁。每次 `createComponent()` 自动执行 `mark()`，`destroyComponent()` 自动执行 `unmark()`：

```python
from architect.component import createComponent, destroyComponent

# 创建 Marker（自动追踪实体创建）
marker = createComponent(entityId, Marker)

# 销毁 Marker（自动追踪实体销毁）
destroyComponent(entityId, Marker)
```

从 v1.1.0 开始，`Marker` 暴露了两个 `EventSignal` 用于监听实体生命周期：

```python
from architect.component import entitiesServer  # 服务端
from architect.component import entitiesClient  # 客户端

# 实体首次标记时
entitiesServer.onEntityCreated.on(lambda entityId: print('Created:', entityId))

# 实体最终取消标记时
entitiesServer.onEntityDestroyed.on(lambda entityId: print('Destroyed:', entityId))
```

---

## 7. 原生组件访问

框架提供了对网易引擎原生组件的简化访问：

```python
from architect.component import NeC, NeS

# 获取引擎原生组件
player_comp = NeC.Player          # '#Player'（客户端原生组件）
item_comp = NeS.Item              # '#Item'（服务端原生组件）
```

`NeC` 和 `NeS` 是常量类，列出了约 50 个常用的客户端和 40 个常用的服务端原生组件名称。

---

## 8. 完整示例：战斗系统

```python
# components/combat.py
from architect.component import Component, PersistKeys
from architect.component.schema import DefineFields, FieldSchema

class Health(Component):
    hp = 100
    maxHp = 100

@DefineFields({
    'attack': FieldSchema(default=10, validator=lambda v: v >= 0),
    'defense': FieldSchema(default=5, validator=lambda v: v >= 0),
})
class CombatStats(Component):
    pass

class Dead(Component):
    """标记死尸组件"""
    pass

# subsystems/combatSystem.py
from architect.core import SubsystemServer, ServerSubsystem, EventListener
from architect.query import Query, EntityId
from architect.component import createComponent, getComponent

class ServerCombatSystem(ServerSubsystem):
    canTick = True

    @EventListener('EntityHurtEvent')
    def onEntityHurt(self, event):
        sourceId = event.srcId
        targetId = event.id
        rawDamage = event.damage

        # 获取攻击方属性
        attacker = getComponent(sourceId, CombatStats)
        atk = attacker.attack if attacker else 5

        # 获取防御方属性
        defender = getComponent(targetId, CombatStats)
        defense = defender.defense if defender else 0

        # 计算最终伤害
        finalDamage = max(1, atk - defense)

        # 应用伤害
        health = getComponent(targetId, Health)
        if health:
            health.hp = max(0, health.hp - finalDamage)
            event.setEvent('damage', finalDamage)

            if health.hp <= 0:
                self.handle_death(targetId)

    def handleDeath(self, entityId):
        createComponent(entityId, Dead)
```

```python
# subsystems/combat_client.py
from architect.core import SubsystemClient, ClientSubsystem
from architect.query import Query, EntityId

class ClientCombatSystem(ClientSubsystem):
    canTick = True

    @Query(Health, EntityId, excluded=[Dead])
    def updateHealthBars(self, health, entityId):
        # 只处理活着的实体
        hpPct = health.hp / max(1, health.maxHp)
        self.show_health_bar(entityId, min(1.0, hpPct))

    def onUpdate(self, dt):
        self.update_health_bars()
```

---

## 下一步

- [事件系统 (event.md)](event.md) — 事件 API 详解
- [子系统 (subsystem.md)](subsystem.md) — 子系统 API
- [最佳实践 (best-practices.md)](best-practices.md) — 组件设计建议