# 服务端MoLang工具 (MolangServer) API

`architect.utils.molang.server` 模块提供了服务端MoLang属性管理和查询广播功能，用于在服务端处理MoLang属性并同步到客户端。

## 依赖

- `.common.MolangMutable` - MoLang可变接口
- `...basic.compServer` - 服务端组件
- `...unreliable.Unreliable` - 不可靠基类
- `...subsystem.ServerSubsystem` - 服务端子系统
- `...subsystem.SubsystemServer` - 服务端子系统装饰器
- `...event.EventListener` - 事件监听器

## 类

### `NamedProperty`

命名属性类，继承自 `MolangMutable` 和 `Unreliable`，提供MoLang属性操作。

#### 构造函数

```python
def __init__(self, name):
```

- **`name`**: 属性名称

#### 属性

- `name`: 属性名称

#### 方法

##### `_molang(actorId)`

获取实体的MoLang组件。

- **`actorId`**: 实体ID
- **返回值**: MoLang组件 (`compServer.CreateQueryVariable(actorId)`)

##### `getValue(actorId)`

获取MoLang属性的值。

- **`actorId`**: 实体ID
- **返回值**: 属性值（如果发生错误返回None）
- **实现**:
  1. 执行MoLang表达式 `"v.property('{}')".format(self.name)`
  2. 如果发生错误，调用 `_handleError` 并返回None
  3. 返回结果值

##### `setValue(actorId, value)`

设置MoLang属性的值。

- **`actorId`**: 实体ID
- **`value`**: 要设置的值
- **实现**: 调用 `self._molang(actorId).SetPropertyValue(self.name, value)`

##### `_handleError(error)`

处理错误（从父类 `Unreliable` 继承）。

## 子系统类

### `MolangServer`

MoLang服务端子系统，继承自 `ServerSubsystem`。

#### 装饰器

`@SubsystemServer` - 标记为服务端子系统

#### 事件监听器

##### `_handleQuery(event)`

处理 'ronin_molang_query' 自定义事件。

- **`event`**: 事件对象，包含查询数据
- **功能**: 将查询事件广播到所有客户端
- **调用**: `self.sendAllClients('ronin_molang_query', event.dict())`

#### 方法

##### `sendQuery(id, name, value)`

发送查询到所有客户端。

- **`id`**: 实体ID
- **`name`**: 查询名称
- **`value`**: 查询值
- **发送事件**: 'ronin_molang_query' 到所有客户端

## 使用示例

### 1. 基本属性管理

```python
from ..architect.utils.molang.server import NamedProperty, MolangServer

class ServerPropertyManager:
    def __init__(self):
        self.properties = {}
        self.entity_properties = {}
        
        # 获取MoLang服务器子系统实例
        self.molang_server = MolangServer.getInstance()
    
    def create_property(self, name):
        """创建命名属性"""
        property_obj = NamedProperty(name)
        self.properties[name] = property_obj
        
        print(f"创建命名属性: {name}")
        return property_obj
    
    def set_entity_property(self, actor_id, prop_name, value):
        """设置实体属性"""
        if prop_name not in self.properties:
            self.create_property(prop_name)
        
        property_obj = self.properties[prop_name]
        property_obj.setValue(actor_id, value)
        
        # 记录实体属性
        if actor_id not in self.entity_properties:
            self.entity_properties[actor_id] = {}
        
        self.entity_properties[actor_id][prop_name] = value
        
        print(f"设置实体 {actor_id} 属性 {prop_name} = {value}")
        
        # 广播到客户端
        if self.molang_server:
            self.molang_server.sendQuery(actor_id, prop_name, value)
        
        return value
    
    def get_entity_property(self, actor_id, prop_name):
        """获取实体属性"""
        if prop_name not in self.properties:
            return None
        
        property_obj = self.properties[prop_name]
        value = property_obj.getValue(actor_id)
        
        return value
    
    def create_entity_stats(self, actor_id):
        """创建实体统计属性"""
        stats = {
            'health': 20,
            'max_health': 20,
            'attack': 5,
            'defense': 3,
            'speed': 1.0
        }
        
        for stat_name, stat_value in stats.items():
            self.set_entity_property(actor_id, stat_name, stat_value)
        
        print(f"创建实体 {actor_id} 统计属性: {stats}")
        return stats
    
    def update_entity_health(self, actor_id, health_change):
        """更新实体生命值"""
        current_health = self.get_entity_property(actor_id, 'health')
        if current_health is None:
            current_health = 20
        
        new_health = max(0, current_health + health_change)
        
        self.set_entity_property(actor_id, 'health', new_health)
        
        print(f"实体 {actor_id} 生命值更新: {current_health} -> {new_health}")
        
        # 检查死亡
        if new_health <= 0:
            self.on_entity_death(actor_id)
        
        return new_health
    
    def on_entity_death(self, actor_id):
        """实体死亡处理"""
        print(f"实体 {actor_id} 死亡")
        
        # 重置属性
        self.reset_entity_properties(actor_id)
        
        # 广播死亡事件
        self.broadcast_entity_event(actor_id, 'death')
    
    def reset_entity_properties(self, actor_id):
        """重置实体属性"""
        default_props = {
            'health': 20,
            'is_alive': 1,
            'combat_state': 0
        }
        
        for prop_name, prop_value in default_props.items():
            self.set_entity_property(actor_id, prop_name, prop_value)
        
        print(f"实体 {actor_id} 属性已重置")
    
    def broadcast_entity_event(self, actor_id, event_type):
        """广播实体事件"""
        event_prop_name = f"event_{event_type}"
        self.set_entity_property(actor_id, event_prop_name, 1)
        
        # 短暂后重置事件标志
        # 这里可以使用定时器或延迟任务
        
        print(f"广播实体 {actor_id} 事件: {event_type}")
    
    def apply_status_effect(self, actor_id, effect_name, duration):
        """应用状态效果"""
        effect_prop_name = f"effect_{effect_name}"
        self.set_entity_property(actor_id, effect_prop_name, 1)
        
        # 设置持续时间
        duration_prop_name = f"effect_{effect_name}_duration"
        self.set_entity_property(actor_id, duration_prop_name, duration)
        
        print(f"对实体 {actor_id} 应用状态效果: {effect_name}, 持续时间: {duration}")
        
        # 开始效果计时
        self.start_effect_timer(actor_id, effect_name, duration)
    
    def start_effect_timer(self, actor_id, effect_name, duration):
        """开始效果计时器"""
        # 这里应该实现定时器逻辑
        # 当时间到达时，移除效果
        
        print(f"开始效果计时: {effect_name} 对实体 {actor_id}, 持续时间: {duration}")
    
    def remove_status_effect(self, actor_id, effect_name):
        """移除状态效果"""
        effect_prop_name = f"effect_{effect_name}"
        self.set_entity_property(actor_id, effect_prop_name, 0)
        
        duration_prop_name = f"effect_{effect_name}_duration"
        self.set_entity_property(actor_id, duration_prop_name, 0)
        
        print(f"移除实体 {actor_id} 状态效果: {effect_name}")
    
    def get_entity_summary(self, actor_id):
        """获取实体摘要"""
        if actor_id not in self.entity_properties:
            return None
        
        summary = {
            'id': actor_id,
            'properties': self.entity_properties[actor_id].copy(),
            'current_health': self.get_entity_property(actor_id, 'health'),
            'is_alive': self.get_entity_property(actor_id, 'is_alive') or 1
        }
        
        # 检查是否有活跃效果
        active_effects = []
        for prop_name in self.entity_properties[actor_id].keys():
            if prop_name.startswith('effect_') and not prop_name.endswith('_duration'):
                if self.get_entity_property(actor_id, prop_name):
                    effect_name = prop_name[7:]  # 移除 'effect_' 前缀
                    active_effects.append(effect_name)
        
        summary['active_effects'] = active_effects
        
        return summary
```

### 2. 游戏状态同步

```python
from ..architect.utils.molang.server import MolangServer

class GameStateSyncer:
    def __init__(self):
        self.game_state = {}
        self.player_states = {}
        self.sync_queue = []
        
        # 获取MoLang服务器子系统
        self.molang_server = MolangServer.getInstance()
    
    def update_game_state(self, state_updates):
        """更新游戏状态"""
        self.game_state.update(state_updates)
        
        # 同步到所有客户端
        self.sync_game_state_to_clients()
        
        print(f"更新游戏状态: {state_updates}")
    
    def sync_game_state_to_clients(self):
        """同步游戏状态到客户端"""
        if not self.molang_server:
            return
        
        # 同步全局游戏状态
        for key, value in self.game_state.items():
            # 使用actor_id 0表示全局状态
            self.molang_server.sendQuery(0, f"game_{key}", value)
        
        print(f"同步游戏状态到客户端: {len(self.game_state)} 个属性")
    
    def update_player_state(self, player_id, state_updates):
        """更新玩家状态"""
        if player_id not in self.player_states:
            self.player_states[player_id] = {}
        
        self.player_states[player_id].update(state_updates)
        
        # 同步到客户端
        self.sync_player_state_to_clients(player_id)
        
        print(f"更新玩家 {player_id} 状态: {state_updates}")
    
    def sync_player_state_to_clients(self, player_id):
        """同步玩家状态到客户端"""
        if not self.molang_server or player_id not in self.player_states:
            return
        
        player_state = self.player_states[player_id]
        
        for key, value in player_state.items():
            prop_name = f"player_{player_id}_{key}"
            self.molang_server.sendQuery(player_id, prop_name, value)
        
        print(f"同步玩家 {player_id} 状态到客户端: {len(player_state)} 个属性")
    
    def set_game_time(self, time_value):
        """设置游戏时间"""
        self.update_game_state({'time': time_value})
    
    def set_game_phase(self, phase_name):
        """设置游戏阶段"""
        phase_mapping = {
            'lobby': 0,
            'preparation': 1,
            'playing': 2,
            'ending': 3
        }
        
        phase_value = phase_mapping.get(phase_name, 0)
        self.update_game_state({'phase': phase_value})
        
        # 根据阶段触发事件
        self.on_game_phase_change(phase_name)
    
    def on_game_phase_change(self, phase_name):
        """游戏阶段变化处理"""
        print(f"游戏阶段变化: {phase_name}")
        
        if phase_name == 'playing':
            self.start_gameplay()
        elif phase_name == 'ending':
            self.end_gameplay()
    
    def start_gameplay(self):
        """开始游戏玩法"""
        print("开始游戏玩法")
        
        # 初始化玩家状态
        for player_id in self.player_states.keys():
            self.initialize_player_for_gameplay(player_id)
    
    def end_gameplay(self):
        """结束游戏玩法"""
        print("结束游戏玩法")
        
        # 计算分数和奖励
        self.calculate_scores()
        
        # 重置玩家状态
        for player_id in self.player_states.keys():
            self.reset_player_after_game(player_id)
    
    def initialize_player_for_gameplay(self, player_id):
        """为游戏玩法初始化玩家"""
        initial_state = {
            'health': 100,
            'score': 0,
            'kills': 0,
            'deaths': 0,
            'ready': 1
        }
        
        self.update_player_state(player_id, initial_state)
        print(f"初始化玩家 {player_id} 为游戏玩法")
    
    def reset_player_after_game(self, player_id):
        """游戏后重置玩家"""
        reset_state = {
            'health': 100,
            'ready': 0,
            'in_game': 0
        }
        
        self.update_player_state(player_id, reset_state)
        print(f"重置玩家 {player_id} 状态")
    
    def calculate_scores(self):
        """计算分数"""
        print("计算游戏分数")
        
        # 这里可以实现分数计算逻辑
        for player_id, state in self.player_states.items():
            score = state.get('score', 0)
            print(f"玩家 {player_id} 分数: {score}")
    
    def handle_player_damage(self, attacker_id, target_id, damage_amount):
        """处理玩家伤害"""
        if target_id not in self.player_states:
            return
        
        current_health = self.player_states[target_id].get('health', 100)
        new_health = max(0, current_health - damage_amount)
        
        self.update_player_state(target_id, {'health': new_health})
        
        print(f"玩家 {attacker_id} 对玩家 {target_id} 造成 {damage_amount} 伤害")
        print(f"玩家 {target_id} 生命值: {current_health} -> {new_health}")
        
        # 更新攻击者数据
        if attacker_id in self.player_states:
            current_damage = self.player_states[attacker_id].get('damage_dealt', 0)
            self.update_player_state(attacker_id, {'damage_dealt': current_damage + damage_amount})
        
        # 检查目标是否死亡
        if new_health <= 0:
            self.handle_player_death(target_id, attacker_id)
    
    def handle_player_death(self, dead_player_id, killer_id=None):
        """处理玩家死亡"""
        print(f"玩家 {dead_player_id} 死亡")
        
        # 更新死亡玩家状态
        self.update_player_state(dead_player_id, {
            'health': 0,
            'is_alive': 0,
            'deaths': self.player_states[dead_player_id].get('deaths', 0) + 1
        })
        
        # 更新击杀者状态
        if killer_id and killer_id in self.player_states:
            self.update_player_state(killer_id, {
                'kills': self.player_states[killer_id].get('kills', 0) + 1
            })
        
        # 广播死亡事件
        self.broadcast_player_event(dead_player_id, 'death')
        
        # 安排重生
        self.schedule_player_respawn(dead_player_id)
    
    def broadcast_player_event(self, player_id, event_type):
        """广播玩家事件"""
        if self.molang_server:
            event_data = {
                'player_id': player_id,
                'event_type': event_type,
                'timestamp': self.game_state.get('time', 0)
            }
            
            # 这里可以使用自定义事件系统
            # 简化：通过MoLang属性广播
            self.molang_server.sendQuery(player_id, f"event_{event_type}", 1)
        
        print(f"广播玩家 {player_id} 事件: {event_type}")
    
    def schedule_player_respawn(self, player_id):
        """安排玩家重生"""
        respawn_time = 5  # 5秒后重生
        
        print(f"安排玩家 {player_id} 在 {respawn_time} 秒后重生")
        
        # 这里应该实现定时器逻辑
        # 当时间到达时，调用 respawn_player(player_id)
    
    def respawn_player(self, player_id):
        """重生玩家"""
        if player_id not in self.player_states:
            return
        
        self.update_player_state(player_id, {
            'health': 100,
            'is_alive': 1
        })
        
        print(f"玩家 {player_id} 已重生")
    
    def get_game_summary(self):
        """获取游戏摘要"""
        summary = {
            'game_state': self.game_state.copy(),
            'player_count': len(self.player_states),
            'players': {}
        }
        
        for player_id, state in self.player_states.items():
            summary['players'][player_id] = {
                'health': state.get('health', 100),
                'score': state.get('score', 0),
                'kills': state.get('kills', 0),
                'deaths': state.get('deaths', 0),
                'is_alive': state.get('is_alive', 1)
            }
        
        return summary
```

### 3. 高级属性同步系统

```python
from ..architect.utils.molang.server import NamedProperty, MolangServer

class AdvancedPropertySyncSystem:
    def __init__(self):
        self.properties = {}
        self.property_groups = {}
        self.sync_handlers = {}
        
        self.molang_server = MolangServer.getInstance()
        
        self.setup_property_groups()
    
    def setup_property_groups(self):
        """设置属性组"""
        self.property_groups = {
            'player_stats': ['health', 'stamina', 'mana', 'level',