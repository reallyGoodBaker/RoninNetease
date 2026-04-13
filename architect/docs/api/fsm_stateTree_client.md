# 客户端状态树 (State Tree Client) API

`architect.fsm.stateTree.client` 模块提供了客户端状态树的实现，包括状态树组件和客户端子系统。

## `StateTreeCompClient` 类

`StateTreeCompClient` 是客户端状态树组件，继承自 `BaseCompClient` 和 `StateTree`。

### 继承

- `BaseCompClient`（客户端组件基类）
- `StateTree`（状态树基类）

### 构造函数

#### `onCreate(self, entityId)`

组件创建时初始化。

- **`entityId`**: (字符串) 实体 ID。

### 属性

#### `enabled`

- **类型**: 布尔值
- **说明**: 是否启用状态树执行。

### 说明

- 组件创建时会自动注册到 `StateTreeClientSubsystem` 中。
- 默认情况下 `enabled` 为 `False`，需要手动启用才能执行状态树逻辑。

## `StateTreeClientSubsystem` 类

`StateTreeClientSubsystem` 是客户端状态树子系统，负责管理所有客户端状态树组件的更新。

### 装饰器

- `@SubsystemClient`：标记为客户端子系统。

### 继承

- `ClientSubsystem`（客户端子系统基类）

### 静态属性

#### `_comps`

- **类型**: 集合 `set[StateTreeCompClient]`
- **说明**: 存储所有 `StateTreeCompClient` 实例的集合。

### 方法

#### `onInit(self)`

子系统初始化时调用。

- 设置 `canTick = True`，允许子系统更新。

#### `onUpdate(self, _)`

子系统更新时调用。

- **`_`**: (任意) 更新参数（未使用）。
- 遍历所有已注册的 `StateTreeCompClient` 实例，如果组件启用 (`enabled` 为 `True`)，则调用其 `execute()` 方法执行状态树逻辑。

## 使用示例

### 1. 创建状态树组件

```python
from ..architect.fsm.stateTree.client import StateTreeCompClient
from ..architect.component import createComponent

# 创建状态树组件
entity_id = 'player_123'
state_tree_comp = createComponent(entity_id, StateTreeCompClient)

# 启用状态树
state_tree_comp.enabled = True

# 添加状态节点（假设 StateTree 有相应方法）
# state_tree_comp.addState('idle', IdleState)
# state_tree_comp.addState('walk', WalkState)
```

### 2. 使用状态树子系统

状态树子系统会自动注册到客户端子系统管理器中，无需手动创建。系统会在每帧更新时自动调用 `onUpdate` 方法。

### 3. 自定义状态类

```python
from ..architect.fsm.stateTree.common import StateNode

class IdleState(StateNode):
    def onEnter(self):
        print('进入空闲状态')
    
    def onUpdate(self):
        # 状态更新逻辑
        pass
    
    def onExit(self):
        print('退出空闲状态')

class WalkState(StateNode):
    def onEnter(self):
        print('进入行走状态')
    
    def onUpdate(self):
        # 状态更新逻辑
        pass
```

## 注意事项

1. **组件注册**: `StateTreeCompClient` 组件创建时会自动注册到子系统中。
2. **启用状态**: 默认情况下组件是禁用的，需要设置 `enabled = True` 才能执行。
3. **子系统更新**: 子系统会在每帧更新所有启用的状态树组件。
4. **状态树逻辑**: 具体的状态树逻辑（状态节点、转换等）由 `StateTree` 基类提供。
5. **客户端专用**: 该模块仅用于客户端环境，服务端应使用 `architect.fsm.stateTree.server` 模块。

## 与通用状态树的关系

`StateTreeCompClient` 继承自 `StateTree`（定义在 `common.py` 中），因此具有状态树的所有功能：

- 状态节点的添加和管理
- 状态转换
- 事件处理
- 并行状态执行

具体功能请参考 [`architect.fsm.stateTree.common`](fsm_stateTree_common.md) 模块的文档。
