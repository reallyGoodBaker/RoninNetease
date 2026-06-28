# Plugins — 系统插件参考

RoninNetease 内置了系统插件（`$vendor.*`），通过 `conf.py` 中的 `PLUGINS` 列表启用。本文档基于实际示例说明动画和输入插件的用法。

---

## 1. 事件系统插件 — `$vendor.event`

### 1.1 概述

封装了事件分发和管理。启用后自动注册客户端/服务端的 `EventReader` 单例组件。

### 1.2 启用

```python
PLUGINS = [
    '$vendor.event',
]
```

### 1.3 EventReader 组件

`EventReader` 是一个单例组件，用于在 `@Sched.Event` 中获取当前事件数据。正确的用法是**在 `@Query` 的位置参数中传入 `EventReader`，框架会自动注入**：

```python
from architect.query import Query
from architect.plugins.event.client import EventReader
from architect.core import Sched

class MySystem(ClientSubsystem):
    @Sched.Event('EntityHurtEvent')
    @Query(EventReader)
    def onEntityHurt(self, reader):
        # reader 是 EventReader 实例，由 @Query 自动注入
        event = reader.event()
        entityId = event.id
        damage = event.damage
        print('Entity %s took %s damage' % (entityId, damage))
```

### 1.4 `EventReader` 属性与方法

```python
event = reader.event()  # 获取当前 ChainedEvent

# ChainedEvent 的常用属性与方法
event.id           # 实体 ID
event.damage       # 伤害值
event.srcId        # 来源实体 ID
event.cause        # 伤害原因
event.stop()       # 停止事件传递
event.prevent()    # 阻止默认行为
event.setEvent(k, v)  # 修改事件字段
event.dict()       # 获取原始 dict
```

### 1.5 服务端用法

```python
from architect.plugins.event.server import EventReader

class MyServerSystem(ServerSubsystem):
    @Sched.Event('EntityHurtEvent')
    @Query(EventReader)
    def onEntityHurt(self, reader):
        event = reader.event()
        if event.damage > 50:
            event.setEvent('damage', 10)
```

---

## 2. 动画扩展插件 — `$vendor.animation`

### 2.1 启用

```python
PLUGINS = ['$vendor.animation']
```

### 2.2 动画映射定义

动画系统使用**短键 → 完整动画路径**的映射模式。在配置模块中定义一个字典：

```python
# assets/animations.py
GenericMapping = {
    'idle':    'animation.standard_steve.idle',
    'walk':    'animation.standard_steve.walk',
    'diamond': 'animation.standard_steve.diamond',
    'stop':    'animation.standard_steve.stop',
    'attack':  'animation.standard_steve.attack.diamond',
}
```

- **键**：短名称，用于代码中播放和停止动画
- **值**：完整的 MC 动画标识符（对应 `.animation.json` 文件中的路径）

### 2.3 动画元数据

```python
# assets/animMeta.py
AnimMeta = {
    "animation.standard_steve.idle": {
        "loop": True,
        "length": 2
    },
    "animation.standard_steve.walk": {
        "loop": True,
        "length": 1
    },
    "animation.standard_steve.attack.diamond": {
        "loop": "hold_on_last_frame",
        "length": 0.4167,
        "notifies": {
            "0.25": [{"name": "attack", "state": 1}],
            "0.375": [{"name": "stun", "state": 0}],
        }
    },
}
```

### 2.4 注册和播放

在子系统中注册元数据、动画映射、配置缓动并播放动画。**播放时使用映射字典的短键和槽位名**：

```python
from architect.plugins.animation.components.animClient import (
    AnimationExComponent, AnimationEasingTypes, AnimationEasingConf
)
from architect.component import getOrCreateComponent, getOneComponent
from architect.core import localPlayerId
from .assets.animations import GenericMapping
from .assets.animMeta import AnimMeta

class MyAnimSystem(ClientSubsystem):
    def onPlayerCreated(self):
        entityId = localPlayerId()
        animEx = getOrCreateComponent(entityId, AnimationExComponent)

        # 必须先注册元数据，再注册动画映射
        animEx.registerMetadatas(AnimMeta)
        animEx.registerAnimations(GenericMapping)
        animEx.updateActorAnimDef()

        # 为每个动画键配置缓动（缓入/缓出）
        for animKey in GenericMapping.keys():
            animEx.registerEasing(
                animKey,
                AnimationEasingConf(1, 0.15, AnimationEasingTypes.SINE),
                AnimationEasingConf(0, 0.24, AnimationEasingTypes.CUBIC),
            )

    def start_walking(self):
        animEx = getOneComponent(localPlayerId(), AnimationExComponent)
        animEx.play('walk', 'loco')    # 键='walk', 槽='loco'

    def stop_walking(self):
        animEx = getOneComponent(localPlayerId(), AnimationExComponent)
        animEx.stop('walk', 'loco')

    def play_attack(self):
        animEx = getOneComponent(localPlayerId(), AnimationExComponent)
        animEx.play('attack', 'holding')  # 键='attack', 槽='holding'
```

> **重要：** `registerMetadatas()` 必须在 `registerAnimations()` 之前调用，否则动画元数据不存在会导致注册失败。元数据由 `editor/tools/animExtractor` 工具从动画 JSON 文件中提取生成 `animMeta.py`。

### 2.5 `@Dispatch` 动画事件分发

`@Dispatch` 接收**完整的动画路径**作为参数，处理类建议继承 `BaseActionDispatcher`。通知回调命名规则为 `notify{Name}{Start|End}`：

```python
from architect.plugins.animation.utils import BaseActionDispatcher, Dispatch
from architect.plugins.animation.components.animClient import AnimationExComponent

@Dispatch('animation.standard_steve.attack.diamond')  # 完整动画路径
class DiamondAttackDispatcher(BaseActionDispatcher):
    def onEnded(self, entityId, animComp):
        # 动画结束（完成或中断）时调用
        animComp.play('diamond', 'holding')  # 回到持剑动画

    def notifyAttackStart(self, entityId, animEx):
        # 对应 AnimMeta 中的 notify 'attack' state=1
        pass

    def notifyStunStart(self, entityId, animEx):
        # 对应 notify 'stun' state=1
        self.movement(entityId, False)  # 禁止移动

    def notifyStunEnd(self, entityId, animEx):
        # 对应 notify 'stun' state=0
        self.movement(entityId, True)

    def onInterrupted(self, entityId, animEx):
        self.movement(entityId, True)

    def onFinish(self, entityId, animEx):
        self.movement(entityId, True)
```

**`AnimationEventDispatcher` 事件回调：**

| 回调 | 签名 | 触发时机 |
|---|---|---|
| `onFinish` | `(self, entityId, animComp)` | 动画正常结束 |
| `onInterrupted` | `(self, entityId, animComp)` | 动画被中断 |
| `onEnded` | `(self, entityId, animComp)` | 动画结束（完成或中断） |
| `notify{Name}Start` | `(self, entityId, animEx)` | 通知状态变为 1 |
| `notify{Name}End` | `(self, entityId, animEx)` | 通知状态变为 0 |

**`BaseActionDispatcher` 提供的基础方法：**

| 方法 | 说明 |
|---|---|
| `movement(entityId, canMove)` | 控制实体移动/跳跃 |
| `cam(entityId, lock)` | 控制摄像机拖拽 |

### 2.6 `AnimationExComponent` 核心方法

| 方法 | 说明 |
|---|---|
| `registerMetadatas(metadata)` | 注册动画元数据 dict（必须在 `registerAnimations` 之前调用） |
| `registerAnimations(mapping)` | 注册动画映射 dict |
| `updateActorAnimDef()` | 应用动画定义到实体 |
| `registerEasing(key, easeIn, easeOut)` | 为动画键注册缓动配置 |
| `play(key, slot)` | 在指定槽位播放动画（key 为映射短键） |
| `stop(key, slot)` | 停止槽位中的动画 |
| `stopAll()` | 停止所有动画 |
| `setPlaybackRate(key, rate)` | 设置动画播放速率 |
| `getPlayingAnimation(key)` | 获取当前播放的动画对象（含 `.playRate` 属性） |

### 2.7 物品切换动画示例

根据手持物品切换动画：

```python
ItemHoldingAnimMapping = {
    'minecraft:diamond_sword': 'diamond',
    'minecraft:wooden_sword': 'wood',
    'minecraft:iron_sword':   'iron',
}

class AnimClient(ClientSubsystem):
    @EventListener()
    def onPlayerSwap(self, ev=events.OnCarriedNewItemChangedClientEvent()):
        itemName = ev.itemDict['newItemName']
        animKey = ItemHoldingAnimMapping.get(itemName, 'idle')
        animEx = getOneComponent(localPlayerId(), AnimationExComponent)
        if animEx:
            animEx.play(animKey, 'holding')  # 在 holding 槽播放
```

**槽位**用于分层动画。同一实体可同时在 `'loco'` 槽（下半身）和 `'holding'` 槽（上半身）播放不同动画。

### 2.8 缓动类型

```python
from architect.plugins.animation.components.animClient import AnimationEasingTypes

# LINEAR, QUAD, CUBIC, QUART, QUINT, SINE, EXPO
```

### 2.9 `clientOnly` 动画与跨端同步

`AnimationExComponent` 在本地玩家 `AddPlayerCreatedClientEvent` 事件触发时**无法修改本地玩家动画**，但可以给其他玩家进入渲染时播放动画。如果需要在所有玩家加载完成时都播放动画，需同时在 `AddPlayerCreatedClientEvent` 和 `OnLocalPlayerStopLoading` 两个事件中播放动画。

这一限制对 `clientOnly` 动画影响最大：跨端同步动画即使在客户端播放失败，也会在广播到自己时重新尝试播放一次。

```python
class MyAnimSystem(ClientSubsystem):
    @EventListener('AddPlayerCreatedClientEvent')
    def onPlayerCreated(self, ev):
        # 对其他进入渲染的玩家有效，但此时无法修改本地玩家动画
        animEx = getOrCreateComponent(ev.entityId, AnimationExComponent)
        animEx.registerMetadatas(AnimMeta)
        animEx.registerAnimations(GenericMapping)
        animEx.updateActorAnimDef()
        animEx.play('idle', 'loco')

    @EventListener('OnLocalPlayerStopLoading')
    def onLocalPlayerStopLoading(self, ev):
        # 本地玩家加载完成，补充播放本地玩家动画
        animEx = getOneComponent(localPlayerId(), AnimationExComponent)
        if animEx:
            animEx.play('idle', 'loco')
```

### 2.10 实体 Molang 变量控制

动画参数通过**动画 JSON 文件**中的 Molang 表达式绑定，不在 Python 代码中设置。动画 JSON 定义示例：

```json
"animation.standard_steve.idle": {
    "loop": true,
    "blend_weight": "v.blendex.standard_steve.idle",
    "anim_time_update": "v.anim_timeex.standard_steve.idle",
    "bones": { ... }
}
```

- `blend_weight` — 绑定到实体变量 `v.blendex.{path}`，用于控制混合权重
- `anim_time_update` — 绑定到 `v.anim_timeex.{path}`，用于控制动画时间
- 通知通过 `notifies` 字段在 JSON 中声明，由 `@Dispatch` 处理类响应

---

## 3. 输入系统插件 — `$vendor.input`

### 3.1 概述

输入系统基于 **Unreal Enhanced Input** 模式，核心概念：
- **InputAction**：声明一个输入动作（名称 + 值类型 + 修饰符）
- **InputMapping**：将物理输入（键盘/手柄/鼠标）绑定到 InputAction，支持修饰符和触发器
- **消费**：`@InputAction` 装饰器监听动作，通过事件对象 `ev.value` 获取输入值

### 3.2 启用

```python
PLUGINS = ['$vendor.input']
```

### 3.3 步骤一：声明输入动作（`assets/inputAction.py`）

**模块级别的独立调用**，`InputAction()` 会注册到全局注册表：

```python
from architect.plugins.input.utils.inputAction import InputAction
from architect.plugins.input.enum import ValueType
from architect.plugins.input.utils.modifier import DeadZone

# 二维轴向输入（WASD 移动）
InputAction('laravelMovement', ValueType.Vector2, modifiers=[
    DeadZone()  # 归一化处理（键盘出现 (1.0,1.0) 时长度归一化）
])

# 双击输入
InputAction('jump', ValueType.Double)
InputAction('startFly', ValueType.Double)
InputAction('stopFly', ValueType.Double)

# 长按输入
InputAction('spying', ValueType.Double)

# 飞行移动
InputAction('flyMove', ValueType.Vector2)
```

**`InputAction` 构造函数：** `InputAction(actionName, valueType, modifiers=[])`

| 参数 | 说明 |
|---|---|
| `actionName` | 动作名称，用作 `@InputAction` 装饰器的匹配键 |
| `valueType` | `ValueType.Double` / `ValueType.Vector2` / `ValueType.Vector3` |
| `modifiers` | 修饰符列表（`DeadZone`, `Negate`, `SwizzleAxis` 等） |

### 3.4 步骤二：定义输入映射（`assets/inputMapping.py`）

**模块级别的独立调用**，`InputMapping()` 注册上下文并绑定物理输入到 InputAction：

```python
from architect.plugins.input.utils.mappingContext import InputMapping, InputBinding
from architect.plugins.input.enum import KeyboardKey, InputType, AxisSwizzleOrder, GamepadAxis, GamepadKey, MouseKey
from architect.plugins.input.utils.modifier import SwizzleAxis, Negate
from architect.plugins.input.utils.trigger import TriggerDown, DoubleTap, TriggerHold

InputMapping('move', [
    # W → laravelMovement (yxz 轴交换 + 按下触发)
    InputBinding(InputType.Key, KeyboardKey.W, 'laravelMovement',
        modifiers=[SwizzleAxis(order=AxisSwizzleOrder.YXZ)],
        triggers=[TriggerDown()]),
    # S → laravelMovement (反向)
    InputBinding(InputType.Key, KeyboardKey.S, 'laravelMovement',
        modifiers=[SwizzleAxis(order=AxisSwizzleOrder.YXZ), Negate()],
        triggers=[TriggerDown()]),
    # D → laravelMovement (x 轴正向)
    InputBinding(InputType.Key, KeyboardKey.D, 'laravelMovement',
        triggers=[TriggerDown()]),
    # A → laravelMovement (x 轴反向)
    InputBinding(InputType.Key, KeyboardKey.A, 'laravelMovement',
        modifiers=[Negate()],
        triggers=[TriggerDown()]),
    # 手柄左摇杆 → laravelMovement
    InputBinding(InputType.Axis, GamepadAxis.LS, 'laravelMovement',
        triggers=[TriggerDown()]),

    # 空格 → jump
    InputBinding(InputType.Key, KeyboardKey.Space, 'jump',
        triggers=[TriggerDown()]),
    # 手柄 A → jump
    InputBinding(InputType.Gamepad, GamepadKey.A, 'jump',
        triggers=[TriggerDown()]),

    # 双击空格 → startFly
    InputBinding(InputType.Key, KeyboardKey.Space, 'startFly',
        triggers=[DoubleTap()]),
    # 双击手柄 A → startFly
    InputBinding(InputType.Gamepad, GamepadKey.A, 'startFly',
        triggers=[DoubleTap()]),
])

# 飞行模式映射
InputMapping('fly', [
    InputBinding(InputType.Key, KeyboardKey.W, 'flyMove',
        modifiers=[SwizzleAxis(order=AxisSwizzleOrder.YXZ)],
        triggers=[TriggerDown()]),
    # ... (同 move 的 WASD 绑定)
    InputBinding(InputType.Key, KeyboardKey.Space, 'stopFly',
        triggers=[DoubleTap()]),
])

# 瞄具模式映射
InputMapping('spying', [
    InputBinding(InputType.Key, MouseKey.Right, 'spying',
        triggers=[TriggerHold(1)]),   # 长按右键 1 秒
    InputBinding(InputType.Axis, GamepadAxis.LT, 'spying',
        triggers=[TriggerHold(1)]),    # 长按 LT 1 秒
])
```

**`InputBinding` 构造函数：** `InputBinding(inputType, key, actionName, modifiers=[], triggers=[])`

| 参数 | 说明 |
|---|---|
| `inputType` | `InputType.Key` / `InputType.Gamepad` / `InputType.Axis` |
| `key` | `KeyboardKey.*` / `GamepadKey.*` / `GamepadAxis.*` / `MouseKey.*` |
| `actionName` | 目标 InputAction 名称 |
| `modifiers` | 输入值修饰符 |
| `triggers` | 触发条件 |

### 3.5 步骤三：启用映射（子系统中）

```python
from architect.plugins.input.components.inputEx import InputExComponent
from architect.component import getOneSingletonComponent

class MySystem(ClientSubsystem):
    @EventListener('OnLocalPlayerStopLoading')
    def onLocalPlayerStopLoading(self, ev):
        inputEx = getOneSingletonComponent(InputExComponent)
        # 启用映射上下文
        inputEx.enableMappings('move', 'spying')

        # 屏蔽原版移动
        operation = LevelClient.getInstance().operation
        operation.SetCanMove(False)
        operation.SetCanJump(False)
```

**`InputExComponent` 映射控制：**

| 方法 | 说明 |
|---|---|
| `enableMapping(name)` | 启用单个映射上下文 |
| `enableMappings(*names)` | 启用多个映射上下文 |
| `disableMapping(name)` | 禁用单个映射上下文 |
| `disableMappings(*names)` | 禁用多个映射上下文 |

### 3.6 步骤四：消费输入（`@InputAction` 装饰器）

```python
from architect.plugins.input.client import InputAction
from architect.plugins.input.enum import InputState

@SubsystemClient
class TestClient(ClientSubsystem):
    @InputAction('laravelMovement')
    def iaMove(self, ev):
        # ev.value 是 Vector2 (x, y)
        x, y = ev.value
        # 将输入转换为世界方向移动...
        motion.SetMotion((mx, my, mz))

    @InputAction('jump')
    def iaJump(self, ev):
        # ev.value 是 Double (0.0 或 1.0)
        if attr.isEntityOnGround():
            motion.SetMotion((x, JUMP_POWER, z))

    @InputAction('startFly')
    def iaStartFly(self, ev):
        inputEx = getOneSingletonComponent(InputExComponent)
        inputEx.disableMapping('move')
        inputEx.enableMapping('fly')

    @InputAction('spying', InputState.Completed)
    def iaCompleteSpying(self, ev):
        # 长按释放时恢复
        LevelClient.getInstance().playerView.SetPlayerFovScale(1)
```

**`@InputAction` 装饰器：**

```python
@InputAction('actionName')                     # 持续触发（每帧）
@InputAction('actionName', InputState.Started)  # 开始按下
@InputAction('actionName', InputState.Completed) # 释放
```

被装饰方法接收一个事件对象 `ev`，其属性：
- `ev.value` — 输入值（`Double` 或 `(x, y)` Vector2 或 `(x, y, z)` Vector3）

### 3.7 修饰符（Modifiers）

在 `InputAction` 或 `InputBinding` 中用于处理原始输入值：

| 修饰符 | 说明 |
|---|---|
| `DeadZone()` | 死区 + 归一化（避免对角线长度超过 1） |
| `Negate()` | 取反（A/D 键实现轴向反向） |
| `SwizzleAxis(order)` | 轴交换（`AxisSwizzleOrder.YXZ` 等） |

**`AxisSwizzleOrder`：** `XYZ`, `XZY`, `YXZ`, `YZX`, `ZXY`, `ZYX`

### 3.8 触发器（Triggers）

在 `InputBinding` 中定义激活条件：

| 触发器 | 说明 |
|---|---|
| `TriggerDown()` | 按下时触发 |
| `DoubleTap()` | 双击触发 |
| `TriggerHold(seconds)` | 长按指定秒数后触发 |

### 3.9 输入类型枚举

```python
from architect.plugins.input.enum import (
    InputType,      # Key(1), Touch(2), Gamepad(3), Axis(4)
    ValueType,      # Double(1), Vector2(2), Vector3(3)
    KeyboardKey,    # A-Z, Space, Lshift, Return, 等
    MouseKey,       # Left(-99), Right(-98), Middle(-97)
    GamepadKey,     # A(1), B(2), X(3), Y(4), Up/Down/Left/Right, LS, RS, LB, RB
    GamepadAxis,    # LS(4096), RS(4097), LT(256), RT(257)
    InputState,     # Empty, Started, Triggered, Completed, Canceled, Ongoing
    AxisSwizzleOrder,
)
```

### 3.10 完整示例

```python
# conf.py
MOD_CLIENT_MODULES = ['assets.inputAction', 'assets.inputMapping', 'testClient']
PLUGINS = ['$vendor.input']
```

```python
# assets/inputAction.py
from architect.plugins.input.utils.inputAction import InputAction
from architect.plugins.input.enum import ValueType
from architect.plugins.input.utils.modifier import DeadZone

InputAction('laravelMovement', ValueType.Vector2, modifiers=[DeadZone()])
InputAction('jump', ValueType.Double)
InputAction('startFly', ValueType.Double)
InputAction('stopFly', ValueType.Double)
InputAction('spying', ValueType.Double)
InputAction('flyMove', ValueType.Vector2)
```

```python
# assets/inputMapping.py
from architect.plugins.input.utils.mappingContext import InputMapping, InputBinding
from architect.plugins.input.enum import KeyboardKey, InputType, AxisSwizzleOrder
from architect.plugins.input.utils.modifier import SwizzleAxis, Negate
from architect.plugins.input.utils.trigger import TriggerDown, DoubleTap, TriggerHold

InputMapping('move', [
    InputBinding(InputType.Key, KeyboardKey.W, 'laravelMovement',
        modifiers=[SwizzleAxis(order=AxisSwizzleOrder.YXZ)], triggers=[TriggerDown()]),
    InputBinding(InputType.Key, KeyboardKey.S, 'laravelMovement',
        modifiers=[SwizzleAxis(order=AxisSwizzleOrder.YXZ), Negate()], triggers=[TriggerDown()]),
    InputBinding(InputType.Key, KeyboardKey.D, 'laravelMovement', triggers=[TriggerDown()]),
    InputBinding(InputType.Key, KeyboardKey.A, 'laravelMovement', modifiers=[Negate()], triggers=[TriggerDown()]),
    InputBinding(InputType.Key, KeyboardKey.Space, 'jump', triggers=[TriggerDown()]),
    InputBinding(InputType.Key, KeyboardKey.Space, 'startFly', triggers=[DoubleTap()]),
])
InputMapping('spying', [
    InputBinding(InputType.Key, KeyboardKey.Lshift, 'spying', triggers=[TriggerHold(1)]),
])
```

```python
# testClient.py
from architect.compact import *
from architect.plugins.input.client import InputAction, InputExComponent
from architect.plugins.input.enum import InputState

@SubsystemClient
class TestClient(ClientSubsystem):
    @EventListener('OnLocalPlayerStopLoading')
    def onLocalPlayerStopLoading(self, ev):
        inputEx = getOneSingletonComponent(InputExComponent)
        inputEx.enableMappings('move', 'spying')
        LevelClient.getInstance().operation.SetCanMove(False)

    @InputAction('laravelMovement')
    def iaMove(self, ev):
        x, y = ev.value
        # 将输入转换为世界方向移动

    @InputAction('jump')
    def iaJump(self, ev):
        if compClient.CreateAttr(localPlayerId()).isEntityOnGround():
            motion = compClient.CreateActorMotion(localPlayerId())
            motion.SetMotion((0, 0.5, 0))
```

---

## 4. 运动系统插件 — `$vendor.motion`

### 4.1 概述

封装了原生 `ActorMotionComponent`，提供玩家运动控制及自动客户端→服务端同步。

### 4.2 启用

```python
PLUGINS = ['$vendor.motion']
```

> `conf.py` 中默认已启用此插件。

### 4.3 PlayerMotionComponent

`PlayerMotionComponent` 是一个单例组件，自动在客户端就绪时创建并绑定到本地玩家。

```python
from architect.component import getOneSingletonComponent
from architect.plugins.motion.playerMotionComp import PlayerMotionComponent

motionComp = getOneSingletonComponent(PlayerMotionComponent)
```

### 4.4 属性与方法

| 属性 | 类型 | 读写 | 说明 |
|---|---|---|---|
| `motion` | `tuple (x, y, z)` | 读/写 | 设置运动向量，**写入时自动同步到服务端** |
| `inputVector` | `tuple` | 只读 | 获取输入向量 |
| `mousePosition` | `tuple` | 只读 | 获取鼠标位置 |

### 4.5 基本用法

```python
from architect.compact import *
from architect.plugins.motion.playerMotionComp import PlayerMotionComponent

@SubsystemClient
class MyMovement(ClientSubsystem):
    @Sched.Update
    def updateMovement(self):
        motionComp = getOneSingletonComponent(PlayerMotionComponent)
        # 读取当前运动
        currentMotion = motionComp.motion
        # 读取输入向量
        inputVec = motionComp.inputVector
        print('Input:', inputVec)
```

### 4.6 设置运动（自动同步）

```python
motionComp = getOneSingletonComponent(PlayerMotionComponent)
# 设置运动向量，自动同步到服务端
motionComp.motion = (1.0, 0.5, 0.0)
```

每次写入 `motion` 属性时，框架自动通过 `remote.client.call` 调用服务端的 `PlayerMotionSyncServer.syncMotion`，服务端再将运动状态应用到对应玩家的 `ActorMotionComponent`。

### 4.7 配合输入系统使用

```python
from architect.plugins.input.client import InputAction
from architect.plugins.motion.playerMotionComp import PlayerMotionComponent

@SubsystemClient
class TestClient(ClientSubsystem):
    @InputAction('laravelMovement')
    def onMove(self, ev):
        x, y = ev.value
        motionComp = getOneSingletonComponent(PlayerMotionComponent)
        motionComp.motion = (x, 0, y)
```

### 4.8 服务端同步

运动同步由 `PlayerMotionSyncServer` 自动处理，无需手动调用。客户端写入 `motion` 时立即触发：

```python
# 位于 architect/plugins/motion/system/sync.py（自动处理，无需手动调用）
@SubsystemServer
class PlayerMotionSyncServer(ServerSubsystem):
    @Remote
    def syncMotion(self, playerId, motion):
        compServer.CreateActorMotion(playerId).SetPlayerMotion(motion)
```

---

## 5. 小队系统插件 — `$vendor.squad`

> 此插件源文件目前为空（预留），尚未实现。

---

## 下一步

- [插件系统 (plugin.md)](plugin.md) — 如何创建自定义插件
- [快速开始 (quickstart.md)](quickstart.md) — 入门教程