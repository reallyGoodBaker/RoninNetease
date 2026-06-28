# FSM — 有限状态机与状态树

RoninNetease 提供两种状态机实现：**StateTree（状态树，推荐）** 和**经典 FSM（已弃用）**。本章重点讲解 StateTree 的核心机制、模块化策略和常见陷阱。

---

## 1. 为什么放弃经典 FSM？

经典 FSM（`architect.fsm.deprecated`）是一个扁平状态机：所有状态平铺在一个字典中，通过 `transitionTo(name)` 手动切换。

### 1.1 经典 FSM 的三大致命缺陷

**① 状态爆炸没有分组**

```python
fsm.addState('idle_ground', ...)
fsm.addState('idle_air', ...)
fsm.addState('walk_ground', ...)
fsm.addState('walk_water', ...)
fsm.addState('attack_ground_sword', ...)
fsm.addState('attack_air_bow', ...)
# 10 个实体动作 × 5 种环境 = 50 个状态，无法复用
```

没有层级概念，idle/walk/attack 是平级的，环境判定（地面/空中/水中）必须嵌入每个状态内部。

**② 状态切换是显式的**

```python
class WalkState(State):
    def onUpdate(self):
        if not isOnGround():
            self.fsm.transitionTo('fall')   # ❌ 必须手动记住切换目标
        if enemyNearby():
            self.fsm.transitionTo('chase')  # ❌ 每加一个状态，所有上游状态都要改
```

每次新增状态，所有可能切换到它的上游状态都要修改 `transitionTo` 调用。状态越多，维护成本指数上升。

**③ 没有 `canEnter`/`canExit` 守卫**

经典 FSM 的 `transitionTo` 只在切换时检查 `canEnter`，但不检查 `canExit`。如果一个状态正在执行回血动画，被外部强制切换到攻击状态，动画就会被截断——经典 FSM 无法阻止这种切换。

### 1.2 StateTree 如何解决

| 问题 | 经典 FSM | StateTree |
|---|---|---|
| 状态分组 | 无，所有状态平铺 | 树形层级，父节点 = 分类/守卫 |
| 切换方式 | 手动 `transitionTo(name)` | 自动深度优先搜索叶子节点 |
| 退出守卫 | 不支持 `canExit` | `canExit()` 可阻止不安全的切换 |
| 上下文复用 | 无 | 父子节点 `setContext/getContext` 继承链 |
| 模块化 | 状态间耦合 | `copy(deep=True)` + 独立树组合 |

---

## 2. StateTree 核心机制

### 2.1 StateNode — 状态节点（完整 API）

`StateNode` 是状态树的**原子单元**。每个节点有名称、父节点引用、子节点列表和上下文字典。框架通过 5 个生命周期钩子驱动节点的行为。

#### 2.1.1 构造函数与属性

```python
from architect.fsm.stateTree.common import StateNode

node = StateNode('myState')
```

| 属性 | 类型 | 初始值 | 说明 |
|---|---|---|---|
| `name` | `str` | `'unknown'` | 节点名称（用于 `findNamedNode` 查找） |
| `_parent` | `StateNode \| None` | `None` | 父节点引用（由 `addChildren` 自动维护） |
| `children` | `list[StateNode]` | `[]` | 子节点列表 |
| `_isLeaf` | `bool` | `True` | 是否叶子节点（有无子节点） |
| `_ctx` | `dict` | `{}` | 上下文键值对（子节点可沿树向上读取父节点上下文） |

#### 2.1.2 生命周期钩子

所有钩子都接收 `tree: StateTree` 参数，用于访问 `entityId`、`stateTicks`、`finishTasks()` 等。

```python
class MyNode(StateNode):
    def canEnter(self, tree):
        """搜索阶段调用：返回 True 允许节点被搜索选中。
        每帧可能被调用多次，❌ 不要写副作用。"""
        return True

    def canExit(self, tree):
        """搜索阶段调用：返回 False 锁死当前节点，阻止搜索继续。
        返回 True 允许退出。"""
        return True

    def enter(self, previous, tree):
        """切换阶段调用：节点被激活时触发。
        previous: 上一个叶子节点（首次进入时为 None）"""
        pass

    def exit(self, nextNode, tree):
        """切换阶段调用：节点被替换时触发。
        nextNode: 即将进入的叶子节点"""
        pass

    def update(self, tree):
        """每帧调用：仅在当前激活路径上（当前叶子及所有祖先）触发。"""
        pass
```

**调用时机对照：**

| 钩子 | 谁调用 | 触发条件 | 每帧次数 |
|---|---|---|---|
| `canEnter` | `searchNode()` 搜索 | 搜索遍历时检查每个节点 | 可能多次 |
| `canExit` | `searchNode()` 搜索 | 当前叶子需要退出时检查 | ≤1 |
| `enter` | `switchNode()` 切换 | 节点变为激活状态 | ≤1 |
| `exit` | `switchNode()` 切换 | 节点失去激活状态 | ≤1 |
| `update` | `execute()` 主循环 | 节点在激活路径上 | 1 |

#### 2.1.3 树操作方法

```python
# 添加子节点（自动设置 _parent，标记本节点为非叶子）
parent.addChildren(child1, child2, child3)

# 移除子节点（自动清除 _parent，若无剩余子节点则恢复 _isLeaf=True）
parent.removeChild(child1)

# 在指定位置插入
parent.insert(0, newChild)

# 替换子节点（保留位置，旧节点脱钩，新节点附加）
parent.replaceChild(oldNode, newNode)

# 递归按名称查找（含自身）
found = root.findNamedNode('attack')
```

**叶子状态自动管理：**
- `addChildren` 被调用 → `self._isLeaf = False`
- `removeChild` 移除最后一个子节点 → `self._isLeaf = True`
- 这是一个纯标记，决定搜索算法是否将节点视为终点。非叶子节点不可被搜索选中。

#### 2.1.4 上下文继承机制

```python
parent = StateNode('weapon')
parent.setContext('damage', 50)
parent.setContext('range', 3.0)

child = StateNode('slash')
parent.addChildren(child)

# getContext 向上查找：自身 → 父节点 → 祖父节点 → ... → None
child.getContext('damage')   # 50   （继承自父节点）
child.getContext('range')    # 3.0  （继承自父节点）
child.getContext('speed')    # None （整个链都没找到）

# 子节点覆盖
child.setContext('damage', 100)
child.getContext('damage')   # 100  （覆盖父节点值）

# 父节点仍为原值
parent.getContext('damage')  # 50
```

`getContext` 的返回值既可以是 Python 基本类型，也可以是函数/方法对象，子节点可以在 `enter` 中读取后直接调用：

```python
class AttackNode(StateNode):
    def enter(self, previous, tree):
        attackFn = self.getContext('onAttack')  # 父节点注入的回调
        if callable(attackFn):
            attackFn(tree.entityId)
```

#### 2.1.5 `copy(deep=True)` — 深复制

```python
original = MyCustomNode('template')
original.setContext('damage', 50)
original.addChildren(StateNode('child1'), StateNode('child2'))

# 深复制：递归复制整棵子树
clone = original.copy(deep=True)
# clone 是一个完全独立的树根：
# - _parent = None
# - 子节点全部递归复制
# - _ctx 键值对保留
# - 自定义属性（如子类的 _can_enter）也被复制

# 浅复制：只复制当前节点，不含子节点
shallow = original.copy(deep=False)
```

**复制策略：**
1. 用 `self.__class__` 创建同类型新实例
2. 复制除 `_parent` / `children` 外的所有 `__dict__` 属性
3. 若 `deep=True`，递归复制子节点并用 `addChildren` 附加

### 2.2 树形结构

```
root
├── ground (非叶子，canEnter: isOnGround)
│   ├── idle    ← 叶子
│   ├── walk    ← 叶子
│   └── attack  ← 叶子
├── air (非叶子，canEnter: not isOnGround)
│   ├── fall    ← 叶子
│   └── glide   ← 叶子
└── stunned (canEnter: isStunned) ← 叶子
```

- **非叶子节点**（ground、air）：`_isLeaf=False`，不出现在最终状态中，仅作为分类/守卫。`canEnter` 返回 False 时整个子树跳过
- **叶子节点**（idle、walk、attack 等）：`_isLeaf=True`，真正的"状态"，每帧只有唯一一个叶子被激活

### 2.3 搜索算法详解

`execute()` 每帧执行三个步骤：

```
1. update 阶段
   → 遍历当前激活路径上所有节点（当前叶子及所有祖先），依次调用 update()

2. searchNode() 阶段
   → 调用 searchNode() 搜索下一个可进入的叶子节点
   → 核心规则：
     a. 当前是叶子 → 在父节点下搜索兄弟节点（按 children 顺序）
     b. 找不到 → 向上回溯到父节点的兄弟，继续搜索
     c. 如果某个祖先的 canEnter() 返回 False，跳过它继续向上
     d. 每一跳都检查 canEnter() 和 canExit()

3. switchNode() 阶段
   → 如果搜索成功，沿路径依次 exit 旧节点 → enter 新节点
```

**搜索示例（假设当前在 idle/ground）：**

```
idle.update() → finishTasks() → 标记 _finished=True

searchNode():
  1. 当前是叶子(idle)，搜索父节点(ground)下的兄弟:
     - walk.canEnter() → True → 找到!
  
  返回: path = [walk]

switchNode():
  1. idle.exit(walk, tree)  ← 退出旧节点
  2. walk.enter(idle, tree) ← 进入新节点
  3. stateTicks = 0         ← 重置计时器
```

**回溯示例（ground 下所有子节点都无法进入 → 向上搜索 air 子树）：**

```
walk 已完成，但 walk 的兄弟 attack.canEnter() → False

searchNode():
  1. ground 下所有兄弟都已尝试，向上回溯
  2. 搜索 root 下 ground 之后的兄弟:
     - air.canEnter(tree) → True (玩家在空中)
     - 递归进入 air 子树，找到 fall.canEnter() → True
  
  返回: path = [air, fall]

switchNode():
  1. walk.exit(fall, tree)   ← 退出 walk
  2. air.enter(walk, tree)    ← 进入 air（非叶子也可以有 enter/exit）
  3. fall.enter(air, tree)    ← 进入 fall
```

**关键细节：**
- `finishTasks()` 是手动调用的，不调用则状态永远不会自动切换
- `canExit()` 返回 False 会**阻止整个搜索**——当前节点被锁死
- 非叶子节点也可以有 `enter`/`exit`，每次穿过时都会触发
- `stateTicks` 在每次 `switchNode` 时归零

### 2.3 StateTree API 参考

#### 构造函数

```python
from architect.fsm.stateTree.common import StateTree

tree = StateTree(entityId)
```

| 参数 | 类型 | 说明 |
|---|---|---|
| `entityId` | `str` | 关联的实体 ID，传递给 hook 和组件 |

#### 树结构管理

| 方法 | 签名 | 说明 |
|---|---|---|
| `getRoot()` | `() -> StateNode` | 获取根节点（自动创建，名为 `'root'`） |
| `setRoot(node)` | `(StateNode) -> None` | 替换根节点，自动清除新节点的 `_parent` |
| `insertNode(node, parent=None)` | `(StateNode, StateNode?) -> StateNode` | 插入节点到指定父节点下（默认根），返回插入的节点 |
| `createNode(parent=None)` | `(StateNode?) -> StateNode` | 创建匿名节点（`name='unknown'`）并插入 |
| `replaceNode(src, target)` | `(StateNode?, StateNode) -> None` | 替换节点。`src=None` 时将 `target` 添加为根的子节点 |
| `replaceNamedNode(name, target)` | `(str, StateNode) -> None` | 按名称查找并替换节点 |
| `findNamedNode(name)` | `(str) -> StateNode \| None` | 递归按名称搜索节点（从根开始） |

#### 状态控制

| 方法 | 签名 | 说明 |
|---|---|---|
| `switchNode(node)` | `(StateNode) -> None` | 强制切换到指定节点（触发 exit/enter，`stateTicks` 归零） |
| `finishTasks()` | `() -> None` | 标记当前任务完成（`_finished=True`），允许下一帧自动搜索 |
| `execute()` | `() -> None` | 主循环：先 update 激活路径上所有节点 → 搜索下一个叶子 → 切换 |
| `reset(clearMapping=False)` | `(bool) -> None` | 重置状态树：清空 `_current`，标记 `_finished`。`clearMapping=True` 额外清空 `mapping` 字典 |

#### 状态查询

| 方法 | 签名 | 返回 | 说明 |
|---|---|---|---|
| `currentState()` | `() -> StateNode \| None` | 当前叶子节点 | 无激活节点时返回 `None` |
| `currentStateName()` | `() -> str \| None` | 当前节点名称 | 无激活节点时返回 `None` |
| `getCurrent()` | `() -> StateNode \| None` | 当前叶子节点 | 同 `currentState()`，驼峰命名 |
| `setCurrent(node)` | `(StateNode) -> None` | — | **直接设置** `_current`（不触发 exit/enter），慎用 |
| `clearCurrent()` | `() -> None` | — | 清空 `_current` |
| `isFinished()` | `() -> bool` | 是否已完成 | `_finished` 为 True 时搜索算法才会尝试切换 |
| `setFinished(val)` | `(bool) -> None` | — | 手动设置 `_finished` 状态 |
| `findAllActivatedStateNodes()` | `() -> list[StateNode]` | 激活路径（从根到当前叶子） | 按从根到叶子的顺序排列 |
| `searchNode()` | `() -> (StateNode, list[StateNode]) \| None` | `(最终叶子, 路径节点列表)` | 执行搜索算法，`_finished=False` 时立即返回 `None` |

#### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `entityId` | `str` | 关联的实体 ID |
| `root` | `StateNode` | 根节点 |
| `stateTicks` | `int` | 当前状态已持续的 tick 数（`switchNode` 时归零，每帧 `execute()` 时递增） |
| `mapping` | `dict` | 用户自定义映射表（框架不使用，供外部存储任意数据） |

### 2.4 基础用法

```python
from architect.fsm.stateTree.common import StateTree, StateNode

# 定义状态
class Idle(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'idle')

    def enter(self, previous, tree):
        pass  # 播放 idle 动画

    def update(self, tree):
        if tree.stateTicks > 60:    # 至少停留 60 tick
            tree.finishTasks()      # 标记完成，允许搜索下一个状态

class Walk(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'walk')

    def canEnter(self, tree):
        return hasMoveInput(tree.entityId)  # 只有有输入才进入

    def update(self, tree):
        if not hasMoveInput(tree.entityId):
            tree.finishTasks()

# 构建树
tree = StateTree(entityId)
idle = Idle()
walk = Walk()
tree.insertNode(idle)        # root → idle
idle.addChildren(walk)       # idle → walk（walk 是 idle 的备选）

tree.switchNode(idle)         # 进入 idle

# 每帧
def onUpdate():
    tree.execute()
```

---

## 3. 模块化 StateTree

StateTree 的核心优势在于**状态可以被组合、拷贝和隔离**。以下是三种模块化策略。

### 3.1 策略一：非叶子节点作为守卫（推荐入门）

将大分类作为非叶子节点，子节点作为具体行为。通过 `canEnter` 自动过滤不可用的子树。

```python
class GroundNode(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'ground')

    def canEnter(self, tree):
        return isOnGround(tree.entityId)  # 地面？

class AirNode(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'air')

    def canEnter(self, tree):
        return not isOnGround(tree.entityId)  # 空中？

class IdleNode(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'idle')

    def update(self, tree):
        if hasInput(tree.entityId):
            tree.finishTasks()

class MoveNode(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'move')

    def canEnter(self, tree):
        return hasInput(tree.entityId)

    def update(self, tree):
        doMove(tree.entityId)
        if not hasInput(tree.entityId):
            tree.finishTasks()

# 构建
tree = StateTree(entityId)
ground = GroundNode()
air = AirNode()

tree.insertNode(ground)        # root → ground
tree.insertNode(air)           # root → air（ground 之后的兄弟）

ground.addChildren(IdleNode())  # ground → idle
ground.addChildren(MoveNode())  # ground → move

air.addChildren(StateNode('fall'))  # air → fall（简单叶子无需自定义类）

tree.switchNode(ground.children[0])  # 从 ground/idle 开始
```

**执行效果：**
- 玩家在地面 → `ground.canEnter` True → 自动搜索 ground 子树 → idle/move 轮流切换
- 玩家跳起 → `ground.canEnter` False → 搜索跳过 ground → 进入 air → fall
- 落地 → `air.canEnter` False → 搜索跳过 air → 回到 ground → 进入 idle

### 3.2 策略二：上下文继承 + copy 复用

`setContext`/`getContext` 提供了**沿树向上继承**的键值对机制。子节点可以读取父节点设置的参数，也可以覆盖。

```python
class ConfigurableAttack(StateNode):
    """可配置的攻击节点（通过 copy 复制出不同伤害的版本）"""
    def __init__(self, damage=10):
        StateNode.__init__(self, 'attack')
        self.setContext('damage', damage)
        self.setContext('range', 3.0)

    def enter(self, previous, tree):
        dmg = self.getContext('damage')
        rng = self.getContext('range')
        print('Attack with damage: %d, range: %.1f' % (dmg, rng))

    def update(self, tree):
        performAttack(self.getContext('damage'), self.getContext('range'))
        tree.finishTasks()

# 从模板复制出不同配置的变体
lightAttack = ConfigurableAttack(damage=5)
heavyAttack = ConfigurableAttack(damage=30)
heavyAttack.setContext('range', 1.5)  # 覆盖 range

# 复制整个子树
comboTree = StateNode('combo')
comboTree.addChildren(lightAttack.copy(deep=True))
comboTree.addChildren(heavyAttack.copy(deep=True))

# 挂到主树上
combatNode = StateNode('combat')
combatNode.addChildren(comboTree)
tree.insertNode(combatNode)
```

**`copy(deep=True)` 的关键特性：**
- 递归复制所有子节点
- 保留子类自定义属性（如 `damage`、`range`）
- 断开 `_parent` 引用 → 返回的是一个独立树根，可以挂到任意位置
- `setContext` 的键值也会被复制

### 3.3 策略三：独立子树 + 动态挂载

对于复杂实体（如 Boss 的多阶段 AI），可以为每个阶段构建独立子树，在 `enter` 时动态挂载。

```python
class Phase1Tree(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'phase1')
        self.addChildren(IdleNode())
        self.addChildren(SweepAttack())

    def enter(self, previous, tree):
        self.hp_threshold = getMaxHp(tree.entityId) * 0.5

    def update(self, tree):
        if getCurrentHp(tree.entityId) < self.hp_threshold:
            tree.finishTasks()

class Phase2Tree(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'phase2')
        self.addChildren(EnrageBuff())
        self.addChildren(AoeAttack())
        self.addChildren(SummonMinions())

class BossAI(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'boss')
        self.phase1 = Phase1Tree()
        self.phase2 = Phase2Tree()

    def enter(self, previous, tree):
        # 当前阶段挂载阶段 1 子树
        self.addChildren(self.phase1.copy(deep=True))

    def exit(self, nextNode, tree):
        if tree.currentStateName() == 'phase1':
            # 阶段 1 结束 → 挂载阶段 2 子树
            self.children = []  # 清空旧子树
            self.addChildren(self.phase2.copy(deep=True))
            # 强制切换到 phase2 的第一个子节点
            tree.switchNode(self.children[0])
```

> **警告：** `self.children = []` 会清空子节点，但不会触发原叶子节点的 `exit` 钩子。如果需要在切换阶段时动画过渡，应在父节点的 `exit` 中显式调用清理逻辑。

### 3.4 策略四：自定义多并发状态树组件

`StateTreeCompServer` 和 `StateTreeCompClient` 本质上是 **StateTree + Component 的组合类**，由内置的 `StateTreeServerSubsystem` / `StateTreeClientSubsystem` 统一驱动。理解它的内部机制后，你可以创建自己的多并发状态树组件。

#### 3.4.1 `StateTreeCompServer` 到底干了什么？

源码只有 10 行，但每一行都很关键：

```python
# architect/fsm/stateTree/server.py（简化）
class StateTreeCompServer(BaseCompServer, StateTree):
    def onCreate(self, entityId):
        StateTree.__init__(self, entityId)          # ① 初始化 StateTree
        StateTreeServerSubsystem._comps.add(self)   # ② 把自己加入全局集合
        self.enabled = False                        # ③ 默认不执行

@SubsystemServer
class StateTreeServerSubsystem(ServerSubsystem):
    _comps = set()  # 全局共享的集合

    def onUpdate(self, dt):
        for comp in StateTreeServerSubsystem._comps:
            if comp.enabled:
                comp.execute()  # ④ 每帧驱动所有已启用的组件
```

**关键设计：**
- ② 步将**所有** `StateTreeCompServer` 实例注册到**同一个**子系统 —— 一个全局桶
- ④ 步子系统的 `onUpdate` 遍历这个桶，逐个调用 `comp.execute()`
- `comp.enabled` 控制了该组件是否被驱动

#### 3.4.2 问题：一个实体只能有一个同名组件

ECS 组件系统中，`getOrCreateComponent(entityId, ComponentClass)` 按**组件类**索引——同一个实体上，每种组件类型只能存在**一个实例**。

这意味着 `StateTreeCompServer` 有一个根本限制：**一个实体只能挂一个状态树**。如果你想让一个实体同时运行"移动 AI"和"战斗 AI"两个独立状态机，单个 `StateTreeCompServer` 是做不到的——你需要创建两个不同名的组件类。

```
getOrCreateComponent(entityId, StateTreeCompServer)  # ✅ 创建一个
getOrCreateComponent(entityId, StateTreeCompServer)  # ⚠️ 返回同一个实例，不是新的
```

另外，对于大型场景（100 个实体），全局桶把所有实例放在一个 `_comps` 集合中，`onUpdate` 串行执行所有 `execute()`。如果你想让不同分组的实体使用不同的子系统（减少单帧遍历量，或加入条件驱动），也需要自定义组件。

#### 3.4.3 创建自定义多并发状态树组件

实现一个实体上同时运行**移动状态树**和**战斗状态树**，各自独立、互不干扰：

**步骤 1：定义自定义组件**

```python
from architect.component import BaseCompServer
from architect.fsm.stateTree.common import StateTree, StateNode

class MovementTreeComp(BaseCompServer, StateTree):
    """移动状态树组件"""
    def onCreate(self, entityId):
        StateTree.__init__(self, entityId)
        # ❌ 不调用 StateTreeServerSubsystem._comps.add(self)
        # ✅ 使用自己的子系统管理
        MovementSubsystem._comps.add(self)

class CombatTreeComp(BaseCompServer, StateTree):
    """战斗状态树组件"""
    def onCreate(self, entityId):
        StateTree.__init__(self, entityId)
        CombatSubsystem._comps.add(self)
```

**步骤 2：定义各自的子系统**

```python
from architect.core.export import SubsystemServer, ServerSubsystem

@SubsystemServer
class MovementSubsystem(ServerSubsystem):
    _comps = set()

    def onInit(self):
        self.canTick = True

    def onUpdate(self, dt):
        for comp in MovementSubsystem._comps:
            comp.execute()  # 只驱动移动状态树

@SubsystemServer
class CombatSubsystem(ServerSubsystem):
    _comps = set()

    def onInit(self):
        self.canTick = True

    def onUpdate(self, dt):
        for comp in CombatSubsystem._comps:
            comp.execute()  # 只驱动战斗状态树
```

**步骤 3：为实体构建双状态树**

```python
from architect.component import getOrCreateComponent

entityId = 'somePlayer'

# 移动状态树：地面/空中 自动切换
moveComp = getOrCreateComponent(entityId, MovementTreeComp)
ground = StateNode('ground')
air = StateNode('air')
moveComp.insertNode(ground)
moveComp.insertNode(air)
ground.addChildren(IdleNode())
ground.addChildren(WalkNode())
air.addChildren(FallNode())
air.addChildren(GlideNode())
moveComp.switchNode(ground.children[0])

# 战斗状态树：完全独立，不受移动状态影响
combatComp = getOrCreateComponent(entityId, CombatTreeComp)
combat = StateNode('combat')
combat.addChildren(SearchNode())
combat.addChildren(ChaseNode())
combat.addChildren(AttackNode())
combatComp.insertNode(combat)
combatComp.switchNode(combat.children[0])
```

**效果：** 两个状态树完全隔离 —— 移动树从 walk 切换到 fall（玩家跳起）时，战斗树仍在 chase 中追敌。各自的状态切换互不影响。

#### 3.4.4 进阶：条件驱动（暂停/恢复）

如果不想让 `onUpdate` 无条件驱动所有组件，可以在子系统中加入条件判断：

```python
@SubsystemServer
class SmartCombatSubsystem(ServerSubsystem):
    _comps = set()

    def onUpdate(self, dt):
        for comp in SmartCombatSubsystem._comps:
            # 只有实体在战斗半径内才驱动战斗状态树
            entityId = comp.entityId
            if not isNearPlayer(entityId, radius=50):
                continue
            comp.execute()
```

这种粒度是使用全局桶的 `StateTreeServerSubsystem` 无法做到的 —— 因为全局桶对所有组件一视同仁。

#### 3.4.5 客户端版本

完全相同的方式，只是替换为 `BaseCompClient` 和 `ClientSubsystem`：

```python
from architect.component import BaseCompClient
from architect.fsm.stateTree.common import StateTree, StateNode
from architect.core.export import SubsystemClient, ClientSubsystem

class UICursorComp(BaseCompClient, StateTree):
    def onCreate(self, entityId):
        StateTree.__init__(self, entityId)
        UICursorSubsystem._comps.add(self)

@SubsystemClient
class UICursorSubsystem(ClientSubsystem):
    _comps = set()

    def onUpdate(self, dt):
        for comp in UICursorSubsystem._comps:
            comp.execute()

# 构建 UI 状态树（指针/拖动/点击）
cursorComp = getOrCreateComponent(localPlayerId(), UICursorComp)
```

---

## 4. StateTree 与经典 FSM 的对照

### 4.1 相同业务，两种实现

**经典 FSM 实现巡逻 AI：**

```python
class IdleState(State):
    def onUpdate(self):
        if self.stateTime > 60:
            if hasEnemy(self.entityId):
                self.fsm.transitionTo('chase')
            else:
                self.fsm.transitionTo('patrol')

class PatrolState(State):
    def onUpdate(self):
        moveToNextWaypoint(self.entityId)
        if reachedWaypoint(self.entityId):
            if hasEnemy(self.entityId):
                self.fsm.transitionTo('chase')
            else:
                self.fsm.transitionTo('idle')

# ❌ 问题：当新增 Flee 状态时，需要修改 Idle 和 Patrol 的 onUpdate
```

**StateTree 实现相同逻辑：**

```python
class BehaviorGroup(StateNode):
    def canEnter(self, tree):
        return True  # 总是可以进入

class Idle(StateNode):
    def update(self, tree):
        if tree.stateTicks > 60:
            tree.finishTasks()  # ← 只标记完成，不关心下一个是什么

class Patrol(StateNode):
    def update(self, tree):
        moveToNextWaypoint(tree.entityId)
        if reachedWaypoint(tree.entityId):
            tree.finishTasks()

class Chase(StateNode):
    def canEnter(self, tree):
        return hasEnemy(tree.entityId)  # ← 有敌人时才进入

    def update(self, tree):
        if not hasEnemy(tree.entityId):
            tree.finishTasks()

# ✅ 新增 Flee 只需加一个节点，无需修改任何已有节点
class Flee(StateNode):
    def canEnter(self, tree):
        return isLowHp(tree.entityId) and hasEnemy(tree.entityId)
```

**核心区别：** 经典 FSM 中状态**知道**它要去哪里（`transitionTo('chase')`），StateTree 中状态只**声明**自己可以结束（`finishTasks()`），由树结构决定下一步。

### 4.2 何时使用经典 FSM

| 场景 | 推荐 |
|---|---|
| 状态 < 5 个，固定流程 | 经典 FSM 也可以（简单直观） |
| 状态 > 5 个，有分类需求 | StateTree |
| 状态需被复用/拷贝 | StateTree（`copy(deep=True)`） |
| 需要非破坏性升级（热更新） | StateTree（可替换子树） |
| 需要客户端/服务端共用逻辑 | StateTree（ECS 组件化） |

---

## 5. 常见陷阱

### 5.1 忘记调用 `finishTasks()`

```python
class StuckState(StateNode):
    def update(self, tree):
        doSomething()
        # ❌ 忘记调用 tree.finishTasks()，状态永远不会切换
```

**正确做法：** 在每个状态的 `update` 中显式标记完成条件。

### 5.2 `canExit` 返回 False 导致死锁

```python
class AttackState(StateNode):
    def canExit(self, tree):
        return self.animationFinished  # 只有动画播完才能退出

    def enter(self, previous, tree):
        self.animationFinished = False
        playAnimation(tree.entityId, 'attack')  # 假设 30 tick

    def update(self, tree):
        if tree.stateTicks > 30:
            self.animationFinished = True
            tree.finishTasks()
```

`canExit` 返回 False 时 `searchNode` 会直接返回 None，状态机卡死。确保 `canExit` 最终会变为 True。

### 5.3 非叶子节点的 `canEnter` 副作用

```python
class BadGuard(StateNode):
    def canEnter(self, tree):
        self.enterCount += 1  # ❌ 副作用！每次搜索都会调用 canEnter
        return True
```

`canEnter` 在**搜索阶段会被多次调用**（每帧可能调用 N 次），不要在其中写有副作用的逻辑。只做纯布尔判断。

### 5.4 `enter` 中调用 `finishTasks`

```python
class InstantNode(StateNode):
    def enter(self, previous, tree):
        tree.finishTasks()  # ❌ 进入后立即标记完成
```

这会导致 `execute()` 在同一帧的搜索阶段就切换走。如果你需要一个"瞬时节点"（只执行 enter 不执行 update），把逻辑放在 `enter` 中并确保 `canExit` 立即返回 True，但不要在同一帧内二次切换（会导致状态闪烁）。

### 5.5 子树清空不清理引用

```python
def exit(self, nextNode, tree):
    self.children = []  # 清空子节点
    # ⚠️ 原来的子节点对象仍存在，只是脱离了树
    # 如果它们持有 compClient/compServer 引用，可能导致内存泄漏
```

**建议：** 如果需要动态替换子树，用 `replaceChild` 而非直接操作 `children` 列表。

---

## 6. StateNodeServer 服务端扩展

服务端节点继承 `StateNodeServer`，提供引擎操作封装：

```python
from architect.fsm.stateTree.server import StateNodeServer

class ServerAttack(StateNodeServer):
    def enter(self, previous, tree):
        entityId = tree.entityId
        self.markVariant(entityId, 2)          # 切换实体变体
        self.playSound(entityId, 'mob.attack') # 播放音效
        self.movement(entityId, False)         # 锁定移动
        self.camera(entityId, True)            # 锁定摄像机

    def exit(self, nextNode, tree):
        self.movement(tree.entityId, True)     # 恢复移动
        self.camera(tree.entityId, False)
```

| 静态方法 | 效果 |
|---|---|
| `markVariant(id, val)` | 设置/获取实体的 MarkVariant |
| `playSound(id, name)` | 在实体位置播放音效（`playsound` 命令） |
| `movement(id, enabled)` | 控制实体移动/跳跃（对玩家用 `inputpermission`，对非玩家调整 `SPEED`） |
| `camera(id, enabled)` | 控制摄像机输入权限（`inputpermission camera`） |

`createChild(name, cls)` 快速创建带子系统引用的子节点：

```python
idle = StateNodeServer('idle')
patrol = idle.createChild('patrol', PatrolNode)  # 自动设置 subsys + addChildren
```

---

## 7. 完整示例：多阶段 Boss AI

```python
from architect.fsm.stateTree.common import StateTree, StateNode
from architect.fsm.stateTree.server import StateNodeServer

class BossIntro(StateNode):
    """出场动画"""
    def __init__(self):
        StateNode.__init__(self, 'intro')

    def canExit(self, tree):
        return tree.stateTicks > 100  # 播放 100 tick 后才能退出

    def enter(self, previous, tree):
        spawnParticles(tree.entityId)

class BossIdle(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'idle')

    def update(self, tree):
        lockOnTarget(tree.entityId)
        if tree.stateTicks > 30:
            tree.finishTasks()

class BossMelee(StateNodeServer):
    def __init__(self):
        StateNodeServer.__init__(self, 'melee')

    def canEnter(self, tree):
        return distanceToTarget(tree.entityId) < 3

    def enter(self, previous, tree):
        entityId = tree.entityId
        self.playSound(entityId, 'mob.boss.attack')
        self.movement(entityId, False)

    def update(self, tree):
        performMelee(tree.entityId)
        if tree.stateTicks > 15:
            tree.finishTasks()

    def exit(self, nextNode, tree):
        self.movement(tree.entityId, True)

class BossRanged(StateNodeServer):
    def __init__(self):
        StateNodeServer.__init__(self, 'ranged')

    def canEnter(self, tree):
        return 3 <= distanceToTarget(tree.entityId) < 15

    def update(self, tree):
        if not canSeeTarget(tree.entityId):
            tree.finishTasks()  # 丢失视野 → 回到 idle
        if tree.stateTicks > 40:
            shootProjectile(tree.entityId)
            tree.finishTasks()

class BossFlee(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'flee')

    def canEnter(self, tree):
        return getHpPercent(tree.entityId) < 0.2

    def update(self, tree):
        fleeFromTarget(tree.entityId)

# === 构建 ===
tree = StateTree(entityId)

intro = BossIntro()
combat = StateNode('combat')         # 非叶子：战斗分组
combat.addChildren(BossIdle())
combat.addChildren(BossMelee())
combat.addChildren(BossRanged())
combat.addChildren(BossFlee())

tree.insertNode(intro)               # root → intro
intro.addChildren(combat)            # intro → combat

tree.switchNode(intro)               # 启动

# 运行流程：
# intro (100tick) → 自动搜索 combat 子节点
# → idle(30tick) → 敌人在近战范围 → melee(15tick)
# → 敌人跑远了 → idle(30tick) → ranged(40tick) → 射击
# → 血量 < 20% → flee（无限循环）

def onUpdate(dt):
    tree.execute()
```

---

## 下一步

- [组件系统 (ecs.md)](ecs.md) — ECS 组件与 StateTree 集成
- [子系统 (subsystem.md)](subsystem.md) — 子系统生命周期
- [最佳实践 (best-practices.md)](best-practices.md) — 状态机设计建议