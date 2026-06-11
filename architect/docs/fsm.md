# FSM — 有限状态机

RoninNetease 提供两种状态机实现：**StateTree（推荐）** 和 **古典 FSM（已弃用）**。

---

## 1. StateTree — 树形状态机（推荐）

`StateTree` 是一种树形结构的状态机，支持：
- **分层状态**：父状态可以包含子状态，形成状态树
- **状态过渡**：定义状态间的转换条件和动作
- **客户端/服务端分离**：每端有独立的状态树管理

### 1.1 架构

```
architect.fsm.stateTree
├── common.py ← TreeState, Transition, StateTree（通用）
├── client.py ← ClientStateTree（客户端）
└── server.py ← ServerStateTree（服务端）
```

### 1.2 定义状态

```python
from architect.fsm.stateTree.common import TreeState, Transition

class IdleState(TreeState):
    def onEnter(self, entity_id):
        """进入状态"""
        print('Entity %s entered Idle' % entity_id)

    def onUpdate(self, entity_id, dt):
        """每帧更新"""
        pass

    def onExit(self, entity_id):
        """离开状态"""
        print('Entity %s exited Idle' % entity_id)

class PatrolState(TreeState):
    def onEnter(self, entity_id):
        print('Entity %s started patrol' % entity_id)

    def onUpdate(self, entity_id, dt):
        # 巡逻逻辑
        pass
```

### 1.3 定义转换

```python
from architect.fsm.stateTree.common import Transition

# 转换条件
def should_chase(entity_id):
    # 检查是否有敌人在视野内
    return has_enemy_in_range(entity_id)

# 转换定义：从 Idle 到 Chase，条件是 should_chase
idle_to_chase = Transition(
    from_state=IdleState,
    to_state=ChaseState,
    condition=should_chase
)

# 无条件转换（进入后立即执行）
auto_to_patrol = Transition(
    from_state=IdleState,
    to_state=PatrolState
)
```

### 1.4 构建状态树

```python
from architect.fsm.stateTree.server import ServerStateTree

# 创建状态树
tree = ServerStateTree()

# 添加状态
tree.add_state(IdleState)
tree.add_state(PatrolState)
tree.add_state(ChaseState)
tree.add_state(CombatState)

# 添加转换
tree.add_transition(Transition(IdleState, PatrolState))
tree.add_transition(Transition(PatrolState, ChaseState, condition=should_chase))
tree.add_transition(Transition(ChaseState, CombatState, condition=is_close_enough))
tree.add_transition(Transition(CombatState, PatrolState, condition=no_enemy))

# 启动状态机
tree.start(entity_id, IdleState)
```

### 1.5 层级状态

```python
# 父状态：Living
class LivingState(TreeState):
    # 可以包含子状态
    pass

# 子状态
class NormalState(TreeState):
    parent = LivingState  # 指定父状态

class InjuredState(TreeState):
    parent = LivingState

# 在 Living 状态下可以在 Normal/Injured 之间切换
# 而 Living → Dead 是跨父状态的转换
```

### 1.6 客户端状态树

```python
from architect.fsm.stateTree.client import ClientStateTree

tree = ClientStateTree()

class ClientIdle(TreeState):
    def onUpdate(self, entity_id, dt):
        # 处理客户端动画
        play_animation(entity_id, 'idle')

tree.add_state(ClientIdle)
tree.start(entity_id, ClientIdle)
```

### 1.7 完整示例：NPC 行为

```python
from architect.fsm.stateTree.server import ServerStateTree
from architect.fsm.stateTree.common import TreeState, Transition
from architect.core import ServerSubsystem, EventListener

# === 定义状态 ===

class Idle(TreeState):
    def onEnter(self, entity_id):
        print('[NPC] Idle')

    def onUpdate(self, entity_id, dt):
        self.timer += dt
        if self.timer > 5.0:
            # 空闲 5 秒后开始巡逻
            self.timer = 0

class Patrol(TreeState):
    def __init__(self):
        self.patrol_index = 0
        self.waypoints = [(0, 64, 0), (10, 64, 0), (10, 64, 10), (0, 64, 10)]

    def onEnter(self, entity_id):
        self.move_to_next(entity_id)

    def onUpdate(self, entity_id, dt):
        if arrived_at_target(entity_id):
            self.move_to_next(entity_id)

    def move_to_next(self, entity_id):
        self.patrol_index = (self.patrol_index + 1) % len(self.waypoints)
        move_entity_to(entity_id, self.waypoints[self.patrol_index])

class Chase(TreeState):
    target = None

    def onEnter(self, entity_id):
        self.target = find_nearest_enemy(entity_id)

    def onUpdate(self, entity_id, dt):
        if self.target:
            move_entity_to(entity_id, get_position(self.target))

class Attack(TreeState):
    def onEnter(self, entity_id):
        attack_entity(entity_id, self.parent.target)

# === 定义转换 ===

def enemy_in_range(entity_id):
    return find_nearest_enemy(entity_id) is not None

def close_enough(entity_id):
    enemy = find_nearest_enemy(entity_id)
    return enemy and distance_to(entity_id, enemy) < 2.0

def enemy_gone(entity_id):
    return find_nearest_enemy(entity_id) is None

transitions = [
    Transition(Idle, Patrol),
    Transition(Patrol, Chase, condition=enemy_in_range),
    Transition(Chase, Attack, condition=close_enough),
    Transition(Attack, Patrol, condition=enemy_gone),
    Transition(Chase, Patrol, condition=enemy_gone),
]

# === 使用 ===

class NPCBehaviorSystem(ServerSubsystem):
    canTick = True

    def onInit(self):
        self.tree = ServerStateTree()
        self.tree.add_state(Idle)
        self.tree.add_state(Patrol)
        self.tree.add_state(Chase)
        self.tree.add_state(Attack)
        for t in transitions:
            self.tree.add_transition(t)

    def init_npc(self, entity_id):
        self.tree.start(entity_id, Idle)

    def onUpdate(self, dt):
        self.tree.update_all(dt)
```

---

## 2. 古典 FSM（已弃用）

> **警告**：此实现已弃用，不推荐在新项目中使用。建议迁移到 StateTree。

### 2.1 结构

```python
from architect.fsm.deprecated import Fsm, State

class MyState(State):
    def onEnter(self):
        """进入状态"""
        pass

    def onUpdate(self):
        """每帧更新"""
        pass

    def onExit(self):
        """离开状态"""
        pass

    def onEvent(self, event_type, event_data):
        """事件处理"""
        pass

class MyFsm(Fsm):
    def onStart(self):
        """状态机启动"""
        pass
```

### 2.2 `State` 基类

| 方法 | 说明 |
|---|---|
| `onEnter()` | 进入状态时 |
| `onExit()` | 离开状态时 |
| `onUpdate()` | 每 Tick |
| `onEvent(type, data)` | 事件处理 |
| `getFsm()` | 获取所属 FSM 实例 |
| `markVariant(value)` | 设置实体 MarkVariant |
| `playSound(name)` | 播放音效（服务端） |
| `movement(enabled)` | 控制移动（服务端） |
| `camera(enabled)` | 控制摄像机（服务端） |

### 2.3 为什么弃用？

古典 FSM 存在以下问题：
- 不支持分层状态，复杂行为需要大量状态枚举
- 不适合嵌入 ECS 架构
- 难以与 `@Query` 等装饰器语法兼容

**迁移建议**：将古典 FSM 的状态逻辑重构为 `TreeState` 子类。

---

## 3. StateTree vs 古典 FSM 对比

| 特性 | StateTree | 古典 FSM |
|---|---|---|
| 层级状态 | ✅ 支持 | ❌ 不支持 |
| ECS 兼容 | ✅ 适合 | ❌ 不推荐 |
| 转换条件 | 函数式条件 | 命令式切换 |
| 多端支持 | ✅ client/server | 基础支持 |
| 维护状态 | ✅ 活跃开发 | ❌ 已弃用 |

---

## 下一步

- [组件系统 (ecs.md)](ecs.md) — ECS 组件
- [子系统 (subsystem.md)](subsystem.md) — 子系统 API
- [最佳实践 (best-practices.md)](best-practices.md) — 状态机设计建议