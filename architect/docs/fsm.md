# FSM — 有限状态机

RoninNetease 提供三种状态机实现：**StateTree（推荐）**、**经典 FSM（已弃用）** 和 **组件化 StateTree（推荐嵌入 ECS）**。

---

## 1. 概述

```
architect.fsm
├── deprecated.py          ← 经典 FSM（已弃用）
└── stateTree/
    ├── common.py          ← StateTree + StateNode（核心）
    ├── client.py          ← StateTreeCompClient + StateTreeClientSubsystem
    └── server.py          ← StateTreeCompServer + StateNodeServer + StateTreeServerSubsystem
```

---

## 2. StateTree — 树形状态机（推荐）

### 2.1 核心概念

`StateTree` 是一个**树形结构**的状态机，每个节点是 `StateNode` 实例。通过 `canEnter`/`canExit` 控制转换条件，通过深度优先搜索自动找到下一个可进入的叶子节点。

### 2.2 StateNode 基础节点

```python
from architect.fsm.stateTree.common import StateNode

class MyState(StateNode):
    def canEnter(self, tree):
        # type: (StateTree) -> bool
        """返回 True 允许进入此节点"""
        return True

    def canExit(self, tree):
        # type: (StateTree) -> bool
        """返回 True 允许退出此节点"""
        return True

    def enter(self, previous, tree):
        # type: (StateNode | None, StateTree) -> None
        """进入节点时调用，previous 是上一个节点（首次为 None）"""
        pass

    def exit(self, next, tree):
        # type: (StateNode | None, StateTree) -> None
        """退出节点时调用，next 是即将进入的节点"""
        pass

    def update(self, tree):
        # type: (StateTree) -> None
        """每帧更新（仅当前节点及其父节点链）"""
        pass
```

### 2.3 节点树操作

```python
from architect.fsm.stateTree.common import StateNode

# 创建节点
root = StateNode('root')
idle = StateNode('idle')
patrol = StateNode('patrol')

# 构建树
root.addChildren(idle)       # idle 成为 root 的子节点
idle.addChildren(patrol)     # patrol 成为 idle 的子节点（多级嵌套）

# 节点关系
print(patrol._parent)         # idle
print(idle.children)         # [patrol]
print(idle._isLeaf)          # False（有子节点）
print(patrol._isLeaf)        # True（叶子节点）
```

**StateNode 方法：**

| 方法 | 说明 |
|---|---|
| `addChildren(*nodes)` | 添加子节点，自动维护 `_parent` 引用 |
| `removeChild(node)` | 移除子节点 |
| `insert(index, node)` | 在指定位置插入子节点 |
| `replaceChild(oldNode, newNode)` | 替换子节点 |
| `findNamedNode(name)` | 按名称递归搜索节点（含自身） |
| `copy(deep=True)` | 深拷贝节点树 |
| `setContext(k, v)` / `getContext(k)` | 节点上下文存取（向上查找父节点） |

### 2.4 StateTree 状态机

```python
from architect.fsm.stateTree.common import StateTree, StateNode

tree = StateTree(entityId)

# 构建节点树
idle = StateNode('idle')
patrol = StateNode('patrol')
tree.insertNode(idle)
idle.addChildren(patrol)

# 手动切换节点
tree.switchNode(idle)         # 进入 idle 节点（触发 exit/enter）
tree.execute()                # 每帧执行：update + 自动搜索下一个可进入的叶子节点

# 状态查询
current = tree.currentState()        # 当前 StateNode
name = tree.currentStateName()       # 当前节点名称（str）
ticks = tree.stateTicks              # 当前状态已持续的 tick 数
finished = tree.isFinished()         # 当前节点是否已结束

# 自定义节点
class Idle(StateNode):
    def enter(self, previous, tree):
        pass

    def update(self, tree):
        if tree.stateTicks > 100:
            tree.finishTasks()  # 标记当前任务完成，允许自动搜索下一个节点
```

**StateTree 方法：**

| 方法 | 说明 |
|---|---|
| `insertNode(node, parent=None)` | 插入节点到指定父节点下 |
| `createNode(parent=None)` | 创建无名节点并插入 |
| `replaceNode(src, target)` | 替换节点（src=None 时替换根节点） |
| `replaceNamedNode(name, target)` | 按名称查找并替换 |
| `switchNode(node)` | 手动切换到指定节点（触发 exit/enter） |
| `execute()` | 每帧执行（update + 自动搜索切换） |
| `searchNode()` | 搜索下一个可进入的叶子节点（返回 `(finalNode, pathNodes)`） |
| `finishTasks()` | 标记当前任务完成 |
| `reset(clearMapping=False)` | 重置状态树 |
| `findNamedNode(name)` | 按名称搜索节点 |
| `findAllActivatedStateNodes()` | 获取当前激活的节点链（含父节点） |
| `currentState()` | 获取当前叶子节点 |
| `currentStateName()` | 获取当前节点名称 |

### 2.5 完整示例：NPC 巡逻 AI

```python
from architect.fsm.stateTree.common import StateTree, StateNode

# === 定义状态节点 ===

class Idle(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'idle')

    def enter(self, previous, tree):
        print('[NPC] Enter Idle')

    def update(self, tree):
        # 空闲一段时间后标记完成，自动搜索 Patrol
        if tree.stateTicks > 60:
            tree.finishTasks()

class Patrol(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'patrol')
        self.waypoint_index = 0

    def enter(self, previous, tree):
        print('[NPC] Start Patrol')

    def update(self, tree):
        # 巡逻逻辑...
        if enemy_nearby(tree.entityId):
            self._want_chase = True
            tree.finishTasks()

    def canExit(self, tree):
        return True  # 允许退出

class Chase(StateNode):
    def __init__(self):
        StateNode.__init__(self, 'chase')

    def canEnter(self, tree):
        return enemy_nearby(tree.entityId)  # 有敌人才进入

    def enter(self, previous, tree):
        print('[NPC] Start Chase')

    def update(self, tree):
        if not enemy_nearby(tree.entityId):
            tree.finishTasks()  # 敌人丢失，回到巡逻

# === 构建和运行 ===

tree = StateTree(entityId)
root = tree.getRoot()

# 构建节点树
idle = StateNode('idle')
patrol = Patrol()
chase = Chase()

tree.insertNode(idle)         # root → idle
idle.addChildren(patrol)      # idle → patrol
idle.addChildren(chase)       # idle → chase

# 启动状态机
tree.switchNode(idle)

# 每帧调用
def onUpdate(dt):
    tree.execute()
```

### 2.6 组件化 StateTree（嵌入 ECS）

服务端和客户端均提供了 `StateTree` + `Component` 的组合：

```python
# 服务端
from architect.fsm.stateTree.server import StateTreeCompServer, StateNodeServer, StateTreeServerSubsystem
# 客户端
from architect.fsm.stateTree.client import StateTreeCompClient, StateTreeClientSubsystem

# 创建 StateTree 组件
comp = getOrCreateComponent(entityId, StateTreeCompServer)
comp.enabled = True  # 启用自动执行

# 构建节点树
root = comp.getRoot()
idle = StateNodeServer('idle')
patrol = StateNodeServer('patrol')
comp.insertNode(idle)
idle.addChildren(patrol)
comp.switchNode(idle)

# 组件模式下，StateTreeServerSubsystem.onUpdate 自动调用所有已启用 comp 的 execute()
```

### 2.7 StateNodeServer 附加功能

`StateNodeServer` 扩展 `StateNode`，提供服务端便捷方法：

```python
from architect.fsm.stateTree.server import StateNodeServer

class AttackState(StateNodeServer):
    def enter(self, previous, tree):
        entityId = tree.entityId
        self.markVariant(entityId, 2)          # 设置 MarkVariant
        self.playSound(entityId, 'mob.attack') # 播放音效
        self.movement(entityId, False)         # 禁止移动
        self.camera(entityId, True)            # 锁定摄像机

    def exit(self, next, tree):
        entityId = tree.entityId
        self.movement(entityId, True)          # 恢复移动

    def update(self, tree):
        # 可通过 self.subsys 访问所属 ServerSubsystem
        pass

    def notifyChildren(self, name, *args):
        # type: (str, Any) -> None
        """通知所有子节点"""
        pass
```

| StateNodeServer 静态方法 | 说明 |
|---|---|
| `markVariant(entityId, value)` | 设置/获取实体的 MarkVariant |
| `playSound(entityId, soundName)` | 在实体位置播放音效 |
| `movement(entityId, enabled)` | 控制实体移动/跳跃权限 |
| `camera(entityId, enabled)` | 控制摄像机输入权限 |

**`createChild(name, cls)`** — 创建指定类型的子节点并自动添加到 children 列表：

```python
idle = StateNodeServer('idle')
patrol_child = idle.createChild('patrol', PatrolClass)  # 自动 addChildren
```

---

## 3. 经典 FSM（已弃用）

> **警告**：此实现已弃用，仅保留用于向后兼容。新项目请使用 StateTree。

### 3.1 结构

```python
from architect.fsm.deprecated import Fsm, State

class MyState(State):
    def onEnter(self):
        """进入状态时调用"""
        pass

    def onExit(self):
        """退出状态时调用"""
        pass

    def onUpdate(self):
        """每帧更新（stateTime 自动递增）"""
        if self.stateTime > 60:
            self.fsm.transitionTo('patrol')

    def onEvent(self, type, data):
        """事件处理"""
        pass

    def getFsm(self):
        """获取所属 FSM 实例"""
        return self.fsm

# 使用
fsm = Fsm(entityId, MyState)          # 创建并设置默认状态
fsm.addState('patrol', PatrolState)   # 添加状态
fsm.addStateMapping({'chase': Chase}) # 批量添加
fsm.transitionTo('patrol')            # 转换状态
fsm.callUpdate()                      # 每帧调用
```

### 3.2 `State` 基类方法

| 方法 | 说明 |
|---|---|
| `onEnter()` | 进入状态时调用 |
| `onExit()` | 退出状态时调用 |
| `onUpdate()` | 每帧更新 |
| `onEvent(type, data)` | 事件处理 |
| `getFsm()` | 获取所属 FSM 实例 |
| `markVariant(value)` | 设置/获取 MarkVariant |
| `playSound(soundName)` | 播放音效（服务端） |
| `movement(enabled)` | 控制移动权限（服务端） |
| `camera(enabled)` | 控制摄像机权限（服务端） |

`stateTime` 属性记录当前状态已持续的帧数（onUpdate 调用次数）。

### 3.3 `Fsm` 类方法

| 方法 | 说明 |
|---|---|
| `addState(name, stateCls)` | 添加状态 |
| `addStateMapping(states)` | 批量添加状态 dict |
| `getState(name)` | 获取状态实例 |
| `transitionTo(name)` | 切换到指定状态（触发 exit/enter） |
| `callUpdate()` | 每帧调用（递增 stateTime + 执行 onUpdate） |

---

## 下一步

- [组件系统 (ecs.md)](ecs.md) — ECS 组件
- [子系统 (subsystem.md)](subsystem.md) — 子系统 API
- [最佳实践 (best-practices.md)](best-practices.md) — 状态机设计建议