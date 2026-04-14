# 服务端状态树 (State Tree Server) API

`architect.fsm.stateTree.server` 模块提供了服务端状态树的实现，包括状态树组件、服务端状态节点和服务端子系统。

## `StateTreeCompServer` 类

`StateTreeCompServer` 是服务端状态树组件，继承自 `BaseCompServer` 和 `StateTree`。

### 继承

- `BaseCompServer`（服务端组件基类）
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

- 组件创建时会自动注册到 `StateTreeServerSubsystem` 中。
- 默认情况下 `enabled` 为 `False`，需要手动启用才能执行状态树逻辑。

## `StateNodeServer` 类

`StateNodeServer` 是服务端状态节点，继承自 `StateNode`，增加了服务端特有的功能。

### 继承

- `StateNode`（通用状态节点基类）

### 构造函数

#### `__init__(self, name='unknown', subsystem=None)`

初始化服务端状态节点。

- **`name`**: (字符串, 默认值 `'unknown'`) 节点名称。
- **`subsystem`**: (`ServerSubsystem`, 默认值 `None`) 关联的子系统。

### 属性

#### `subsys`

- **类型**: `ServerSubsystem` 或 `None`
- **说明**: 关联的子系统。

### 静态方法

#### `markVariant(entityId, value=None)`

设置或获取实体的标记变体 (Mark Variant)。

- **`entityId`**: (字符串) 实体 ID。
- **`value`**: (整数, 可选) 要设置的标记变体值。如果为 `None`，则返回当前值。
- **返回值**: 如果 `value` 为 `None`，返回当前标记变体值；否则返回 `None`。

#### `playSound(entityId, soundName)`

播放声音。

- **`entityId`**: (字符串) 实体 ID。
- **`soundName`**: (字符串) 声音名称。

#### `movement(entityId, enabled=True)`

启用或禁用实体移动。

- **`entityId`**: (字符串) 实体 ID。
- **`enabled`**: (布尔值, 默认值 `True`) 是否启用移动。

#### `camera(entityId, enabled=True)`

启用或禁用实体相机控制。

- **`entityId`**: (字符串) 实体 ID。
- **`enabled`**: (布尔值, 默认值 `True`) 是否启用相机控制。

### 实例方法

#### `createChild(self, name, cls)`

创建子节点。

- **`name`**: (字符串) 子节点名称。
- **`cls`**: (类, 默认值 `StateNodeServer`) 子节点类。
- **返回值**: (`StateNodeServer`) 新创建的子节点。

## `StateTreeServerSubsystem` 类

`StateTreeServerSubsystem` 是服务端状态树子系统，负责管理所有服务端状态树组件的更新。

### 装饰器

- `@SubsystemServer`：标记为服务端子系统。

### 继承

- `ServerSubsystem`（服务端子系统基类）

### 静态属性

#### `_comps`

- **类型**: 集合 `set[StateTreeCompServer]`
- **说明**: 存储所有 `StateTreeCompServer` 实例的集合。

### 方法

#### `onInit(self)`

子系统初始化时调用。

- 设置 `canTick = True`，允许子系统更新。

#### `onUpdate(self, _)`

子系统更新时调用。

- **`_`**: (任意) 更新参数（未使用）。
- 遍历所有已注册的 `StateTreeCompServer` 实例，如果组件启用 (`enabled` 为 `True`)，则调用其 `execute()` 方法执行状态树逻辑。

## 使用示例

### 1. 创建服务端状态树组件

```python
from ..architect.fsm.stateTree.server import StateTreeCompServer, StateNodeServer
from ..architect.component import createComponent

# 创建状态树组件
entity_id = 'player_123'
state_tree_comp = createComponent(entity_id, StateTreeCompServer)

# 启用状态树
state_tree_comp.enabled = True

# 创建服务端状态节点
idle_node = StateNodeServer('idle')
walk_node = StateNodeServer('walk')

# 构建层次结构
state_tree_comp.insertNode(idle_node)
idle_node.addChildren(walk_node)
```

### 2. 使用服务端特有功能

```python
class AttackState(StateNodeServer):
    def enter(self, previous, tree):
        # 播放攻击声音
        self.playSound(tree.entityId, 'attack.sound')
        
        # 禁用移动
        self.movement(tree.entityId, False)
        
        # 设置标记变体
        self.markVariant(tree.entityId, 2)
    
    def exit(self, next, tree):
        # 恢复移动
        self.movement(tree.entityId, True)
        
        # 重置标记变体
        self.markVariant(tree.entityId, 0)
```

### 3. 自定义状态类

```python
class CustomServerState(StateNodeServer):
    def __init__(self, name, damage):
        super().__init__(name)
        self.damage = damage
    
    def canEnter(self, tree):
        # 检查实体是否存活
        from ...basic import compServer
        health = compServer.CreateAttr(tree.entityId).GetAttrValue(AttrType.HEALTH)
        return health > 0
    
    def enter(self, previous, tree):
        print(f'进入服务端状态: {self.name}, 伤害: {self.damage}')
        
        # 使用子系统（如果提供了）
        if self.subsys:
            self.subsys.broadcast('state_entered', {'state': self.name})
```

## 注意事项

1. **服务端专用**: 该模块仅用于服务端环境，客户端应使用 `architect.fsm.stateTree.client` 模块。
2. **组件注册**: `StateTreeCompServer` 组件创建时会自动注册到子系统中。
3. **启用状态**: 默认情况下组件是禁用的，需要设置 `enabled = True` 才能执行。
4. **子系统更新**: 子系统会在每帧更新所有启用的状态树组件。
5. **服务端功能**: `StateNodeServer` 提供了服务端特有的功能，如播放声音、控制移动和相机等。
6. **子系统关联**: 可以通过 `subsys` 属性访问关联的子系统，用于广播事件等操作。

## 与客户端状态树的差异

| 特性 | 服务端 (`architect.fsm.stateTree.server`) | 客户端 (`architect.fsm.stateTree.client`) |
|------|-------------------------------------------|-------------------------------------------|
| 组件基类 | `BaseCompServer` | `BaseCompClient` |
| 节点基类 | `StateNodeServer`（扩展了服务端功能） | `StateNode`（通用） |
| 子系统装饰器 | `@SubsystemServer` | `@SubsystemClient` |
| 子系统基类 | `ServerSubsystem` | `ClientSubsystem` |
| 服务端功能 | 支持 `markVariant`、`playSound`、`movement`、`camera` 等 | 无服务端特有功能 |
| 适用环境 | 服务端脚本 | 客户端脚本 |
