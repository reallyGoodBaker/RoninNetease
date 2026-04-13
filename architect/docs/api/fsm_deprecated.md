# 已弃用的有限状态机 (FSM Deprecated) API

`architect.fsm.deprecated` 模块提供了一个经典的有限状态机 (FSM) 框架，但已标记为不推荐使用。该模块设计用于临时场景，不建议在 ECS 架构中嵌入。

## 警告

> **注意**: 此模块已标记为弃用。建议使用更现代的 `stateTree` 模块或其他状态管理方案。

## `State` 类

`State` 类是状态机中单个状态的基类。

### 构造函数

#### `__init__(self, fsm)`

初始化状态。

- **`fsm`**: (`Fsm`) 所属的状态机实例。

### 属性

#### `entityId`

- **类型**: 字符串
- **说明**: 状态机关联的实体 ID。

#### `fsm`

- **类型**: `Fsm`
- **说明**: 所属的状态机实例。

#### `stateTime`

- **类型**: 整数
- **说明**: 状态持续时间（以更新次数计）。

### 方法

#### `onEvent(self, type, data)`

处理事件。

- **`type`**: (字符串) 事件类型。
- **`data`**: (任意) 事件数据。

#### `onEnter(self)`

状态进入时调用。

#### `onExit(self)`

状态退出时调用。

#### `onUpdate(self)`

状态更新时调用。

#### `getFsm(self)`

获取所属的状态机实例。

- **返回值**: (`Fsm`) 状态机实例。

#### `markVariant(self, value=None)`

设置或获取实体的标记变体 (Mark Variant)。

- **`value`**: (整数, 可选) 要设置的标记变体值。如果为 `None`，则返回当前值。
- **返回值**: 如果 `value` 为 `None`，返回当前标记变体值；否则返回 `None`。

#### `playSound(self, soundName)`

播放声音（仅服务端）。

- **`soundName`**: (字符串) 声音名称。

#### `movement(self, enabled=True)`

启用或禁用实体移动（仅服务端）。

- **`enabled`**: (布尔值, 默认值 `True`) 是否启用移动。

#### `camera(self, enabled=True)`

启用或禁用实体相机控制（仅服务端）。

- **`enabled`**: (布尔值, 默认值 `True`) 是否启用相机控制。

## `Fsm` 类

`Fsm` 类是有限状态机的主类，管理状态转换和更新。

### 继承

- 继承自 `Unreliable`（不可靠基类）。

### 构造函数

#### `__init__(self, entityId, defaultStateCls, name='default')`

初始化状态机。

- **`entityId`**: (字符串) 关联的实体 ID。
- **`defaultStateCls`**: (类) 默认状态类。
- **`name`**: (字符串, 默认值 `'default'`) 默认状态名称。

### 属性

#### `entityId`

- **类型**: 字符串
- **说明**: 关联的实体 ID。

#### `states`

- **类型**: 字典
- **说明**: 状态名称到状态实例的映射。

#### `defaultState`

- **类型**: `State`
- **说明**: 默认状态实例。

#### `currentState`

- **类型**: `State`
- **说明**: 当前状态实例。

#### `currentStateName`

- **类型**: 字符串
- **说明**: 当前状态名称。

#### `defaultStateName`

- **类型**: 字符串
- **说明**: 默认状态名称。

#### `context`

- **类型**: 字典
- **说明**: 状态机上下文数据。

### 方法

#### `onCreated(self)`

状态机创建时调用（可重写）。

#### `addState(self, name, stateCls)`

添加状态。

- **`name`**: (字符串) 状态名称。
- **`stateCls`**: (类) 状态类。

#### `addStateMapping(self, states)`

批量添加状态。

- **`states`**: (字典) 状态名称到状态类的映射。

#### `getState(self, name)`

获取状态实例。

- **`name`**: (字符串) 状态名称。
- **返回值**: (`State`) 状态实例。

#### `transitionTo(self, name)`

转换到指定状态。

- **`name`**: (字符串) 目标状态名称。
- **返回值**: (布尔值) 是否成功转换。

#### `_callExit(self, state)`

内部方法，调用状态的 `onExit` 方法。

- **`state`**: (`State`) 状态实例。
- **返回值**: (布尔值) 是否成功退出。

#### `_callEnter(self, state)`

内部方法，调用状态的 `onEnter` 方法。

- **`state`**: (`State`) 状态实例。
- **返回值**: (布尔值) 是否成功进入。

#### `callUpdate(self)`

调用当前状态的 `onUpdate` 方法。

## 使用示例

```python
from ..architect.fsm.deprecated import Fsm, State

# 定义状态类
class IdleState(State):
    def onEnter(self):
        print('进入空闲状态')
    
    def onUpdate(self):
        if self.stateTime > 100:
            self.fsm.transitionTo('walk')

class WalkState(State):
    def onEnter(self):
        print('进入行走状态')
        self.movement(True)

# 创建状态机
entity_id = 'player_123'
fsm = Fsm(entity_id, IdleState, 'idle')
fsm.addState('walk', WalkState)

# 状态转换
fsm.transitionTo('walk')

# 更新状态机
fsm.callUpdate()
```

## 注意事项

1. **弃用警告**: 此模块已标记为弃用，不建议在新项目中使用。
2. **ECS 不兼容**: 该 FSM 设计不是基于 ECS 的，与架构的组件系统不兼容。
3. **服务端限制**: 部分功能（如 `movement`、`camera`）仅限服务端使用。
4. **错误处理**: 状态转换和更新使用 `tryCall` 进行错误处理，失败时会回退到默认状态。
5. **状态时间**: `stateTime` 在每次 `callUpdate` 时递增，可用于计时。
