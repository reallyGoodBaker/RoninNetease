# 通用状态树 (State Tree Common) API

`architect.fsm.stateTree.common` 模块提供了状态树的核心实现，包括 `StateTree` 和 `StateNode` 类。这是状态树系统的基础模块，客户端和服务端状态树都基于此实现。

## 概述

状态树是一种层次化的有限状态机，允许状态嵌套和并行执行。与传统的 FSM 相比，状态树提供了更灵活的状态管理能力，但灵活性略低于经典 FSM。

## `StateTree` 类

`StateTree` 类是状态树的主类，管理状态节点的层次结构和状态转换。

### 继承

- 继承自 `Unreliable`（不可靠基类）。

### 构造函数

#### `__init__(self, entityId)`

初始化状态树。

- **`entityId`**: (字符串) 关联的实体 ID。

### 属性

#### `entityId`

- **类型**: 字符串
- **说明**: 关联的实体 ID。

#### `root`

- **类型**: `StateNode`
- **说明**: 根节点。

#### `mapping`

- **类型**: 字典
- **说明**: 节点映射（用途待定）。

#### `_current`

- **类型**: `StateNode` 或 `None`
- **说明**: 当前激活的节点。

#### `_finished`

- **类型**: 布尔值
- **说明**: 状态树是否已完成当前任务。

#### `stateTicks`

- **类型**: 整数
- **说明**: 状态持续时间（以更新次数计）。

### 主要方法

#### `reset(self, clearMapping=False)`

重置状态树。

- **`clearMapping`**: (布尔值, 默认值 `False`) 是否清除节点映射。

#### `findNamedNode(self, name)`

按名称查找节点。

- **`name`**: (字符串) 节点名称。
- **返回值**: (`StateNode` 或 `None`) 找到的节点。

#### `insertNode(self, node, parent=None)`

插入节点到指定父节点下。

- **`node`**: (`StateNode`) 要插入的节点。
- **`parent`**: (`StateNode`, 默认值 `None`) 父节点，如果为 `None` 则插入到根节点。
- **返回值**: (`StateNode`) 插入的节点。

#### `createNode(self, parent=None)`

创建新节点并插入。

- **`parent`**: (`StateNode`, 默认值 `None`) 父节点。
- **返回值**: (`StateNode`) 新创建的节点。

#### `replaceNode(self, src, target)`

替换节点。

- **`src`**: (`StateNode`) 要替换的源节点。
- **`target`**: (`StateNode`) 目标节点。

#### `replaceNamedNode(self, name, target)`

按名称替换节点。

- **`name`**: (字符串) 要替换的节点名称。
- **`target`**: (`StateNode`) 目标节点。

#### `switchNode(self, node)`

切换到指定节点。

- **`node`**: (`StateNode`) 目标节点。

#### `finishTasks(self)`

标记状态树任务已完成。

#### `searchNode(self)`

搜索下一个可以进入的叶子节点。

- **返回值**: 如果找到，返回 `(finalNode, pathNodes)` 元组；否则返回 `None`。

#### `execute(self)`

执行状态树搜索并切换。

#### `currentState(self)`

获取当前状态节点。

- **返回值**: (`StateNode` 或 `None`) 当前节点。

#### `currentStateName(self)`

获取当前状态节点名称。

- **返回值**: (字符串或 `None`) 当前节点名称。

### 访问器和修改器

#### `setRoot(self, node)`

设置根节点。

- **`node`**: (`StateNode`) 新的根节点。

#### `getRoot(self)`

获取根节点。

- **返回值**: (`StateNode`) 根节点。

#### `setCurrent(self, node)`

设置当前节点。

- **`node`**: (`StateNode`) 当前节点。

#### `getCurrent(self)`

获取当前节点。

- **返回值**: (`StateNode` 或 `None`) 当前节点。

#### `clearCurrent(self)`

清除当前节点。

#### `setFinished(self, val)`

设置完成状态。

- **`val`**: (布尔值) 是否完成。

#### `isFinished(self)`

检查是否完成。

- **返回值**: (布尔值) 是否完成。

## `StateNode` 类

`StateNode` 类是状态树中的单个节点。

### 构造函数

#### `__init__(self, name='unknown')`

初始化状态节点。

- **`name`**: (字符串, 默认值 `'unknown'`) 节点名称。

### 属性

#### `name`

- **类型**: 字符串
- **说明**: 节点名称。

#### `_parent`

- **类型**: `StateNode` 或 `None`
- **说明**: 父节点。

#### `children`

- **类型**: 列表
- **说明**: 子节点列表。

#### `_isLeaf`

- **类型**: 布尔值
- **说明**: 是否为叶子节点。

#### `_ctx`

- **类型**: 字典
- **说明**: 节点上下文数据。

### 主要方法

#### `canEnter(self, tree)`

检查节点是否可以进入。

- **`tree`**: (`StateTree`) 状态树实例。
- **返回值**: (布尔值) 是否可以进入。

#### `canExit(self, tree)`

检查节点是否可以退出。

- **`tree`**: (`StateTree`) 状态树实例。
- **返回值**: (布尔值) 是否可以退出。

#### `enter(self, previous, tree)`

节点进入时调用。

- **`previous`**: (`StateNode`) 上一个节点。
- **`tree`**: (`StateTree`) 状态树实例。

#### `exit(self, next, tree)`

节点退出时调用。

- **`next`**: (`StateNode`) 下一个节点。
- **`tree`**: (`StateTree`) 状态树实例。

#### `update(self, tree)`

节点更新时调用。

- **`tree`**: (`StateTree`) 状态树实例。

#### `addChildren(self, *nodes)`

添加子节点。

- **`*nodes`**: (`StateNode`) 要添加的子节点。

#### `removeChild(self, node)`

移除子节点。

- **`node`**: (`StateNode`) 要移除的子节点。

#### `insert(self, index, node)`

在指定位置插入子节点。

- **`index`**: (整数) 插入位置。
- **`node`**: (`StateNode`) 要插入的节点。

#### `replaceChild(self, oldNode, newNode)`

替换子节点。

- **`oldNode`**: (`StateNode`) 要替换的旧节点。
- **`newNode`**: (`StateNode`) 新节点。

#### `findNamedNode(self, name)`

按名称查找节点（递归搜索）。

- **`name`**: (字符串) 节点名称。
- **返回值**: (`StateNode` 或 `None`) 找到的节点。

#### `copy(self, deep=True)`

复制节点。

- **`deep`**: (布尔值, 默认值 `True`) 是否深度复制（包括子节点）。
- **返回值**: (`StateNode`) 节点副本。

#### `setContext(self, k, v)`

设置上下文数据。

- **`k`**: (字符串) 键。
- **`v`**: (任意) 值。

#### `getContext(self, k)`

获取上下文数据（支持继承父节点的上下文）。

- **`k`**: (字符串) 键。
- **返回值**: (任意) 值，如果不存在则返回 `None`。

## 辅助函数

### `nodePathStr(paths)`

将节点路径转换为字符串。

- **`paths`**: (列表) 节点列表。
- **返回值**: (字符串) 路径字符串，格式为 `"节点1 -> 节点2 -> ..."`。

## 使用示例

### 1. 创建状态树

```python
from ..architect.fsm.stateTree.common import StateTree, StateNode

# 创建状态树
entity_id = 'player_123'
tree = StateTree(entity_id)

# 创建状态节点
idle_node = StateNode('idle')
walk_node = StateNode('walk')
run_node = StateNode('run')

# 构建层次结构
tree.insertNode(idle_node)  # 插入到根节点
idle_node.addChildren(walk_node, run_node)

# 设置自定义状态类
class CustomState(StateNode):
    def canEnter(self, tree):
        return True
    
    def enter(self, previous, tree):
        print(f'进入状态: {self.name}')
    
    def update(self, tree):
        print(f'更新状态: {self.name}')
```

### 2. 状态转换

```python
# 切换到指定节点
tree.switchNode(walk_node)

# 执行状态树搜索和切换
tree.execute()

# 获取当前状态
current = tree.currentState()
print(f'当前状态: {current.name if current else None}')
```

### 3. 自定义状态逻辑

```python
class AttackState(StateNode):
    def __init__(self, name='attack'):
        super().__init__(name)
        self.attack_count = 0
    
    def canEnter(self, tree):
        # 只有攻击次数小于3次才能进入
        return self.attack_count < 3
    
    def enter(self, previous, tree):
        print(f'开始攻击，已攻击次数: {self.attack_count}')
    
    def update(self, tree):
        self.attack_count += 1
        print(f'攻击次数: {self.attack_count}')
        
        # 攻击3次后自动退出
        if self.attack_count >= 3:
            tree.finishTasks()
    
    def exit(self, next, tree):
        print('攻击结束')
        self.attack_count = 0  # 重置攻击次数
```

## 搜索算法

状态树使用复杂的搜索算法来寻找下一个可进入的叶子节点：

1. **深度优先搜索**: 从当前节点开始，按子节点顺序搜索。
2. **兄弟节点搜索**: 如果当前叶子节点需要切换，首先搜索同父节点的兄弟节点。
3. **向上回溯**: 如果兄弟节点都不可进入，向上回溯到父节点，继续搜索。
4. **条件检查**: 搜索过程中会检查每个节点的 `canEnter` 和 `canExit` 条件。

## 注意事项

1. **叶子节点**: 只有叶子节点才能被激活，非叶子节点仅用于组织层次结构。
2. **状态转换**: 状态转换通过 `switchNode` 方法实现，会自动调用 `exit` 和 `enter` 方法。
3. **错误处理**: 使用 `tryCall` 包装状态方法调用，避免异常影响状态树运行。
4. **上下文继承**: 节点可以通过 `getContext` 方法访问父节点的上下文数据。
5. **状态更新**: 激活的节点（当前节点及其所有父节点）会在每次 `execute` 时调用 `update` 方法。
