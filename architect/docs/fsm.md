# 状态机 (architect.fsm)

提供了一个经典的有限状态机框架（**不推荐**在 ECS 中使用，建议使用组件模式替代）。

## 定义状态

```python
from architect.fsm.deprecated import State, Fsm

class IdleState(State):
    def onEnter(self):
        print('Enter idle')

    def onExit(self):
        print('Exit idle')

    def onUpdate(self):
        # 每帧更新逻辑
        pass

    def onEvent(self, type, data):
        # 处理事件
        pass

class AttackState(State):
    def onEnter(self):
        print('Enter attack')
```

## 使用状态机

```python
# 创建状态机
fsm = Fsm(entityId, IdleState, name='ai')

# 添加状态
fsm.addState('attack', AttackState)
# 或批量添加
fsm.addStateMapping({
    'idle': IdleState,
    'attack': AttackState,
})

# 状态切换
fsm.transitionTo('attack')

# 每帧更新
fsm.callUpdate()
```

## State 内置实用方法

```python
class MyState(State):
    def onEnter(self):
        # 获取 FSM 宿主实体 ID
        self.entityId

        # 切换 MarkVariant（实体变体）
        self.markVariant(1)    # 设置
        variant = self.markVariant()  # 获取

        # 播放音效
        self.playSound('minecraft:entity.player.attack')

        # 控制实体移动权限
        self.movement(enabled=False)   # 禁用移动
        self.movement(enabled=True)    # 启用移动

        # 控制摄像机权限
        self.camera(enabled=False)     # 禁用摄像机控制