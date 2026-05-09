# 客户端MoLang工具 (MolangClient) API

`architect.utils.molang.client` 模块提供了客户端MoLang查询变量和反应式查询功能，用于在客户端处理MoLang表达式和动画。

## 依赖

- `...unreliable.Unreliable` - 不可靠基类
- `...basic.compClient` - 客户端组件
- `...basic.clientApi` - 客户端API
- `.common.MolangMutable` - MoLang可变基类
- `...subsystem.ClientSubsystem` - 客户端子系统
- `...subsystem.SubsystemClient` - 客户端子系统装饰器
- `...event.core.EventSignal` - 事件信号
- `...event.EventListener` - 事件监听器

## 全局变量

### `_queryVariableUsed`

记录查询变量使用情况的字典。

- **类型**: `dict[str, set]`

### `LevelQuery`

级别查询变量组件。

- **类型**: `compClient.CreateQueryVariable(clientApi.GetLevelId())`

## 函数

### `_recordQueryVariableUsage(name, actorId)`

记录查询变量的使用情况。

- **`name`**: 查询变量名称
- **`actorId`**: 实体ID

## 类

### `QueryVariable`

查询变量类，继承自 `MolangMutable` 和 `Unreliable`。

#### 构造函数

```python
def __init__(self, name, defaultValue=0):
```

- **`name`**: 变量名称（会自动添加 'query.mod.' 前缀）
- **`defaultValue`**: 默认值（默认0）

#### 属性

- `name`: 完整变量名称（带 'query.mod.' 前缀）
- `rawName`: 原始变量名称
- `defaultValue`: 默认值
- `OnValueChanged`: 值变化事件信号

#### 方法

##### `_molangComp(actorId)`

获取实体的MoLang组件。

- **`actorId`**: 实体ID
- **返回值**: MoLang组件

##### `getValue(actorId)`

获取查询变量的值。

- **`actorId`**: 实体ID
- **返回值**: 变量值

##### `setValue(actorId, value)`

设置查询变量的值。

- **`actorId`**: 实体ID
- **`value`**: 要设置的值
- **返回值**: 设置结果
- **触发事件**: `OnValueChanged.emit(actorId, value)`

### `ReactiveQueryVariable`

反应式查询变量类，继承自 `QueryVariable`。

#### 构造函数

```python
def __init__(self, name, calc=None):
```

- **`name`**: 变量名称
- **`calc`**: 计算函数（可选）

#### 方法

##### `update(actorId)`

更新查询变量的值。

- **`actorId`**: 实体ID
- **调用**: `self.setValue(actorId, self.calc(actorId))`

## 全局字典

### `reactiveQueryVariables`

反应式查询变量字典。

- **类型**: `dict[str, ReactiveQueryVariable]`

## 内部函数

### `_addReactiveQueryVariable(name, calc=None, onUpdate=None)`

添加反应式查询变量。

- **`name`**: 变量名称
- **`calc`**: 计算函数（必须可调用）
- **`onUpdate`**: 更新回调函数（可选）

### `_updateReactiveQuery(actorId, name, value)`

更新反应式查询。

- **`actorId`**: 实体ID
- **`name`**: 变量名称
- **`value`**: 值
- **注意**: 如果actorId是本地玩家ID，则不更新

## 子系统类

### `MolangClient`

MoLang客户端子系统，继承自 `ClientSubsystem`。

#### 装饰器

`@SubsystemClient` - 标记为客户端子系统

#### 事件监听器

##### `onQuery(event)`

处理 'ronin_molang_query' 自定义事件。

- **`event`**: 事件对象，包含 `actorId`, `name`, `value`

#### 方法

##### `onInit()`

初始化子系统。

- **设置**: `self.canTick = True`

##### `broadcastQuery(actorId, name, value)`

广播查询变量到服务器。

- **`actorId`**: 实体ID
- **`name`**: 变量名称
- **`value`**: 值
- **发送事件**: 'ronin_molang_query' 到服务器

##### `onRender(_)`

渲染时更新反应式查询变量。

- **遍历**: `_queryVariableUsed` 中的所有变量和实体
- **更新**: 每个实体的反应式查询变量

## 装饰器函数

### `MolangQuery(shared=False)`

MoLang查询装饰器，用于创建反应式查询变量。

#### 参数

- **`shared`**: 是否共享查询（默认False）

#### 用法

```python
@MolangQuery(shared=True)
def my_query_function(actorId):
    # 计算查询值
    return calculated_value
```

#### 内部逻辑

1. 如果 `shared=True`，创建带广播功能的反应式查询变量
2. 如果 `shared=False`，创建普通的反应式查询变量
3. 使用函数名作为查询变量名称

## 使用示例

### 1. 基本查询变量使用

```python
from ..architect.utils.molang.client import QueryVariable, MolangClient

class EntityMoLangManager:
    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.query_vars = {}
        
        # 初始化MoLang客户端子系统
        self.molang_client = MolangClient.getInstance()
        
    def create_query_variable(self, name, default_value=0):
        """创建查询变量"""
        query_var = QueryVariable(name, default_value)
        self.query_vars[name] = query_var
        
        # 监听值变化
        query_var.OnValueChanged.on(self.on_query_value_changed)
        
        print(f"创建查询变量: {name}, 默认值: {default_value}")
        return query_var
    
    def on_query_value_changed(self, actor_id, value):
        """查询变量值变化回调"""
        print(f"实体 {actor_id} 的查询变量值变化: {value}")
        
        # 可以在这里触发其他逻辑
        if value > 10:
            self.on_high_value(actor_id, value)
    
    def on_high_value(self, actor_id, value):
        """高值处理"""
        print(f"警告: 实体 {actor_id} 的查询变量值过高: {value}")
        
        # 可以触发视觉效果或声音
        self.trigger_visual_effect(actor_id)
    
    def trigger_visual_effect(self, actor_id):
        """触发视觉效果"""
        # 这里可以添加粒子效果或动画
        print(f"为实体 {actor_id} 触发视觉效果")
    
    def set_entity_health_query(self, health_value):
        """设置实体生命值查询"""
        health_query = self.create_query_variable('health', health_value)
        
        # 设置当前值
        health_query.setValue(self.entity_id, health_value)
        
        return health_query
    
    def set_entity_speed_query(self, speed_value):
        """设置实体速度查询"""
        speed_query = self.create_query_variable('speed', speed_value)
        speed_query.setValue(self.entity_id, speed_value)
        
        return speed_query
    
    def update_entity_queries(self):
        """更新实体所有查询变量"""
        for name, query_var in self.query_vars.items():
            current_value = query_var.getValue(self.entity_id)
            print(f"查询变量 {name}: {current_value}")
            
            # 可以根据需要更新值
            # query_var.setValue(self.entity_id, new_value)
    
    def broadcast_shared_query(self, query_name, value):
        """广播共享查询"""
        if self.molang_client:
            self.molang_client.broadcastQuery(self.entity_id, query_name, value)
            print(f"广播共享查询: {query_name} = {value}")
```

### 2. 反应式查询变量使用

```python
from ..architect.utils.molang.client import (
    MolangQuery, reactiveQueryVariables, MolangClient
)

class ReactiveMoLangSystem:
    def __init__(self):
        self.entity_states = {}
        self.setup_reactive_queries()
        
    def setup_reactive_queries(self):
        """设置反应式查询"""
        # 注册反应式查询变量
        self.register_health_query()
        self.register_speed_query()
        self.register_combat_state_query()
        
        print("反应式查询设置完成")
    
    @MolangQuery(shared=True)
    def entity_health(self, actor_id):
        """实体生命值查询"""
        # 从实体状态获取生命值
        state = self.entity_states.get(actor_id, {})
        health = state.get('health', 20)
        
        # 可以添加复杂的计算逻辑
        if state.get('is_poisoned', False):
            health *= 0.8  # 中毒效果
        
        return health
    
    @MolangQuery(shared=True)
    def entity_speed(self, actor_id):
        """实体速度查询"""
        state = self.entity_states.get(actor_id, {})
        base_speed = state.get('base_speed', 1.0)
        
        # 计算速度修正
        speed_modifier = 1.0
        
        if state.get('is_slowed', False):
            speed_modifier *= 0.5
        
        if state.get('is_hasted', False):
            speed_modifier *= 1.5
        
        if state.get('is_in_water', False):
            speed_modifier *= 0.7
        
        return base_speed * speed_modifier
    
    @MolangQuery(shared=False)
    def entity_combat_state(self, actor_id):
        """实体战斗状态查询（不共享）"""
        state = self.entity_states.get(actor_id, {})
        
        # 战斗状态编码
        # 0: 空闲, 1: 攻击, 2: 防御, 3: 逃跑
        if state.get('is_attacking', False):
            return 1
        elif state.get('is_defending', False):
            return 2
        elif state.get('is_fleeing', False):
            return 3
        else:
            return 0
    
    def update_entity_state(self, actor_id, state_updates):
        """更新实体状态"""
        if actor_id not in self.entity_states:
            self.entity_states[actor_id] = {}
        
        self.entity_states[actor_id].update(state_updates)
        
        # 触发反应式查询更新
        self.trigger_reactive_updates(actor_id)
        
        print(f"实体 {actor_id} 状态更新: {state_updates}")
    
    def trigger_reactive_updates(self, actor_id):
        """触发反应式查询更新"""
        # 获取MoLang客户端
        molang_client = MolangClient.getInstance()
        
        if molang_client:
            # 手动触发渲染更新
            # 实际应用中，系统会自动在渲染时更新
            pass
    
    def get_reactive_query_value(self, actor_id, query_name):
        """获取反应式查询值"""
        query_var = reactiveQueryVariables.get(query_name)
        
        if query_var:
            return query_var.getValue(actor_id)
        
        return None
    
    def set_reactive_query_callback(self, query_name, callback):
        """设置反应式查询回调"""
        query_var = reactiveQueryVariables.get(query_name)
        
        if query_var and callable(callback):
            query_var.OnValueChanged.on(callback)
            print(f"为查询 {query_name} 设置回调")
            return True
        
        return False
    
    def monitor_entity_health(self, actor_id):
        """监控实体生命值"""
        def on_health_changed(changed_actor_id, health_value):
            if changed_actor_id == actor_id:
                print(f"实体 {actor_id} 生命值变化: {health_value}")
                
                # 生命值低警告
                if health_value < 5:
                    print(f"警告: 实体 {actor_id} 生命值过低!")
                
                # 生命值恢复
                if health_value > 15 and health_value < 20:
                    print(f"实体 {actor_id} 生命值正在恢复")
        
        # 设置回调
        self.set_reactive_query_callback('entity_health', on_health_changed)
    
    def create_entity_with_queries(self, actor_id, initial_state):
        """创建带查询的实体"""
        # 更新实体状态
        self.update_entity_state(actor_id, initial_state)
        
        # 监控生命值
        self.monitor_entity_health(actor_id)
        
        # 获取初始查询值
        health = self.get_reactive_query_value(actor_id, 'entity_health')
        speed = self.get_reactive_query_value(actor_id, 'entity_speed')
        combat_state = self.get_reactive_query_value(actor_id, 'entity_combat_state')
        
        print(f"实体 {actor_id} 创建完成:")
        print(f"  生命值: {health}")
        print(f"  速度: {speed}")
        print(f"  战斗状态: {combat_state}")
        
        return {
            'health': health,
            'speed': speed,
            'combat_state': combat_state
        }
```

### 3. 动画和视觉效果集成

```python
from ..architect.utils.molang.client import (
    QueryVariable, MolangClient, MolangQuery
)

class AnimationMoLangController:
    def __init__(self):
        self.animation_queries = {}
        self.particle_queries = {}
        self.sound_queries = {}
        
        self.setup_animation_queries()
    
    def setup_animation_queries(self):
        """设置动画查询"""
        # 创建动画相关查询变量
        self.animation_queries['walk_speed'] = QueryVariable('anim_walk_speed', 0)
        self.animation_queries['jump_height'] = QueryVariable('anim_jump_height', 0)
        self.animation_queries['attack_strength'] = QueryVariable('anim_attack_strength', 0)
        
        # 设置变化回调
        for name, query in self.animation_queries.items():
            query.OnValueChanged.on(self.on_animation_query_changed)
        
        print("动画查询设置完成")
    
    def on_animation_query_changed(self, actor_id, value):
        """动画查询变化回调"""
        # 这里可以触发动画更新
        print(f"实体 {actor_id} 动画查询变化: {value}")
        
        # 根据值调整动画
        self.adjust_animation(actor_id, value)
    
    def adjust_animation(self, actor_id, value):
        """调整动画"""
        # 这里可以调用动画系统API
        # 例如：设置动画速度、混合权重等
        pass
    
    @MolangQuery(shared=True)
    def entity_animation_blend(self, actor_id):
        """实体动画混合查询"""
        # 计算动画混合权重
        # 可以根据实体状态动态计算
        
        # 示例：根据移动速度计算行走/奔跑混合
        state = self.get_entity_state(actor_id)
        speed = state.get('speed', 0)
        
        if speed < 0.1:
            return 0.0  # 空闲
        elif speed < 0.5:
            return 0.3  # 行走
        else:
            return 1.0  # 奔跑
    
    @MolangQuery(shared=True)
    def entity_particle_intensity(self, actor_id):
        """实体粒子强度查询"""
        state = self.get_entity_state(actor_id)
        
        # 根据实体状态计算粒子强度
        intensity = 0.0
        
        if state.get('is_on_fire', False):
            intensity += 0.8
        
        if state.get('is_magic_active', False):
            intensity += 0.5
        
        if state.get('is_charged', False):
            intensity += 0.3
        
        return min(intensity, 1.0)
    
    @MolangQuery(shared=True)
    def entity_sound_volume(self, actor_id):
        """实体声音音量查询"""
        state = self.get_entity_state(actor_id)
        
        # 基础音量
        volume = 1.0
        
        # 距离衰减（简化）
        distance = state.get('distance_to_player', 10)
        if distance > 20:
            volume *= 0.5
        elif distance > 50:
            volume *= 0.2
        
        # 环境影响
        if state.get('is_underwater', False):
            volume *= 0.7
        
        return volume
    
    def get_entity_state(self, actor_id):
        """获取实体状态（示例）"""
        # 这里应该从实体管理系统获取实际状态
        # 返回示例状态
        return {
            'speed': 0.3,
            'is_on_fire': False,
            'is_magic_active': True,
            'is_charged': False,
            'distance_to_player': 15,
            'is_underwater': False
        }
    
    def update_entity_animation(self, actor_id, animation_data):
        """更新实体动画"""
        # 设置动画查询值
        for query_name, value in animation_data.items():
            if query_name in self.animation_queries:
                self.animation_queries[query_name].setValue(actor_id, value)
        
        print(f"实体 {actor_id} 动画更新: {animation_data}")
    
    def trigger_special_effect(self, actor_id, effect_type):
        """触发特殊效果"""
        effect_queries = {
            'explosion': ('anim_explosion_strength', 1.0),
            'heal': ('anim_heal_intensity', 0.8),
            'teleport': ('anim_teleport_distortion', 0.6),
            'shield': ('anim_shield_strength', 0.9)
        }
        
        if effect_type in effect_queries:
            query_name, value = effect_queries[effect_type]
            
            # 创建临时查询变量
            temp