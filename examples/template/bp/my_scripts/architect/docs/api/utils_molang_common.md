# 通用MoLang工具 (MolangCommon) API

`architect.utils.molang.common` 模块提供了跨客户端和服务端的通用MoLang变量功能，包括命名变量和基础MoLang操作。

## 依赖

- `...basic.isServer` - 检查是否在服务端
- `...basic.compClient` - 客户端组件
- `...basic.compServer` - 服务端组件
- `...unreliable.Unreliable` - 不可靠基类
- `.types.MolangReadable` - MoLang可读接口
- `.types.MolangMutable` - MoLang可变接口

## 类

### `NamedVariable`

命名变量类，继承自 `Unreliable` 和 `MolangMutable`，提供跨客户端的MoLang变量操作。

#### 构造函数

```python
def __init__(self, name):
```

- **`name`**: 变量名称

#### 属性

- `name`: 变量名称

#### 方法

##### `_molangComp(actorId)`

获取实体的MoLang组件（根据运行环境选择客户端或服务端组件）。

- **`actorId`**: 实体ID
- **返回值**: MoLang组件
- **逻辑**:
  - 如果在服务端: `compServer.CreateQueryVariable(actorId)`
  - 如果在客户端: `compClient.CreateQueryVariable(actorId)`

##### `getValue(actorId, defaultValue=0)`

获取MoLang变量的值。

- **`actorId`**: 实体ID
- **`defaultValue`**: 默认值（当发生错误时返回，默认0）
- **返回值**: 变量值
- **实现**:
  1. 获取MoLang组件
  2. 执行MoLang表达式 `'v.' + self.name`
  3. 如果发生错误，调用 `_handleError` 并返回默认值
  4. 返回结果值

##### `setValue(actorId, value)`

设置MoLang变量的值。

- **`actorId`**: 实体ID
- **`value`**: 要设置的值
- **实现**:
  1. 获取MoLang组件
  2. 执行MoLang表达式 `'variable.{} = {};'.format(self.name, value)`

##### `_handleError(error)`

处理错误（从父类 `Unreliable` 继承）。

## 使用示例

### 1. 基本命名变量使用

```python
from ..architect.utils.molang.common import NamedVariable

class MoLangVariableManager:
    def __init__(self):
        self.variables = {}
        self.entity_variables = {}
    
    def create_variable(self, name, initial_value=0):
        """创建命名变量"""
        variable = NamedVariable(name)
        self.variables[name] = variable
        
        print(f"创建命名变量: {name}")
        return variable
    
    def set_entity_variable(self, actor_id, var_name, value):
        """设置实体变量"""
        if var_name not in self.variables:
            self.create_variable(var_name)
        
        variable = self.variables[var_name]
        variable.setValue(actor_id, value)
        
        # 记录实体变量
        if actor_id not in self.entity_variables:
            self.entity_variables[actor_id] = {}
        
        self.entity_variables[actor_id][var_name] = value
        
        print(f"设置实体 {actor_id} 变量 {var_name} = {value}")
    
    def get_entity_variable(self, actor_id, var_name, default=0):
        """获取实体变量"""
        if var_name not in self.variables:
            return default
        
        variable = self.variables[var_name]
        value = variable.getValue(actor_id, default)
        
        return value
    
    def create_health_variable(self):
        """创建生命值变量"""
        health_var = self.create_variable('health', 20)
        return health_var
    
    def create_speed_variable(self):
        """创建速度变量"""
        speed_var = self.create_variable('speed', 1.0)
        return speed_var
    
    def create_custom_variable(self, name, default_value):
        """创建自定义变量"""
        custom_var = self.create_variable(name, default_value)
        return custom_var
    
    def update_entity_health(self, actor_id, health_change):
        """更新实体生命值"""
        current_health = self.get_entity_variable(actor_id, 'health', 20)
        new_health = max(0, current_health + health_change)
        
        self.set_entity_variable(actor_id, 'health', new_health)
        
        print(f"实体 {actor_id} 生命值更新: {current_health} -> {new_health}")
        return new_health
    
    def apply_speed_modifier(self, actor_id, modifier):
        """应用速度修正"""
        current_speed = self.get_entity_variable(actor_id, 'speed', 1.0)
        new_speed = current_speed * modifier
        
        self.set_entity_variable(actor_id, 'speed', new_speed)
        
        print(f"实体 {actor_id} 速度修正: {current_speed} * {modifier} = {new_speed}")
        return new_speed
    
    def batch_update_variables(self, actor_id, variable_updates):
        """批量更新变量"""
        results = {}
        
        for var_name, value in variable_updates.items():
            self.set_entity_variable(actor_id, var_name, value)
            results[var_name] = value
        
        print(f"实体 {actor_id} 批量更新变量: {results}")
        return results
    
    def monitor_variable_changes(self, actor_id, var_name, callback):
        """监控变量变化"""
        # 注意：NamedVariable 没有内置的变化事件
        # 需要定期检查或使用其他机制
        
        def check_variable():
            current_value = self.get_entity_variable(actor_id, var_name)
            # 这里可以比较前后值并调用回调
            # 实际实现需要状态跟踪
            
            return current_value
        
        print(f"开始监控实体 {actor_id} 变量 {var_name}")
        return check_variable
    
    def export_entity_variables(self, actor_id):
        """导出实体所有变量"""
        if actor_id not in self.entity_variables:
            return {}
        
        variables = {}
        for var_name in self.variables.keys():
            value = self.get_entity_variable(actor_id, var_name)
            variables[var_name] = value
        
        print(f"导出实体 {actor_id} 变量: {variables}")
        return variables
    
    def import_entity_variables(self, actor_id, variable_data):
        """导入实体变量"""
        for var_name, value in variable_data.items():
            self.set_entity_variable(actor_id, var_name, value)
        
        print(f"导入实体 {actor_id} 变量: {len(variable_data)} 个")
        return True
```

### 2. 游戏状态管理

```python
from ..architect.utils.molang.common import NamedVariable

class GameStateManager:
    def __init__(self):
        self.state_variables = {}
        self.player_states = {}
        self.setup_game_variables()
    
    def setup_game_variables(self):
        """设置游戏变量"""
        # 游戏全局变量
        self.state_variables['game_time'] = NamedVariable('game_time')
        self.state_variables['game_difficulty'] = NamedVariable('game_difficulty')
        self.state_variables['weather_intensity'] = NamedVariable('weather_intensity')
        
        # 玩家状态变量
        self.state_variables['player_health'] = NamedVariable('player_health')
        self.state_variables['player_stamina'] = NamedVariable('player_stamina')
        self.state_variables['player_mana'] = NamedVariable('player_mana')
        
        # 游戏进度变量
        self.state_variables['quest_progress'] = NamedVariable('quest_progress')
        self.state_variables['level_completion'] = NamedVariable('level_completion')
        
        print("游戏变量设置完成")
    
    def set_game_time(self, time_value):
        """设置游戏时间"""
        # 假设 actor_id 0 表示全局
        self.state_variables['game_time'].setValue(0, time_value)
        print(f"设置游戏时间: {time_value}")
    
    def get_game_time(self):
        """获取游戏时间"""
        time_value = self.state_variables['game_time'].getValue(0, 0)
        return time_value
    
    def set_game_difficulty(self, difficulty_level):
        """设置游戏难度"""
        self.state_variables['game_difficulty'].setValue(0, difficulty_level)
        print(f"设置游戏难度: {difficulty_level}")
    
    def get_game_difficulty(self):
        """获取游戏难度"""
        difficulty = self.state_variables['game_difficulty'].getValue(0, 1)
        return difficulty
    
    def update_player_state(self, player_id, state_data):
        """更新玩家状态"""
        if player_id not in self.player_states:
            self.player_states[player_id] = {}
        
        # 更新状态数据
        self.player_states[player_id].update(state_data)
        
        # 更新MoLang变量
        if 'health' in state_data:
            self.state_variables['player_health'].setValue(player_id, state_data['health'])
        
        if 'stamina' in state_data:
            self.state_variables['player_stamina'].setValue(player_id, state_data['stamina'])
        
        if 'mana' in state_data:
            self.state_variables['player_mana'].setValue(player_id, state_data['mana'])
        
        print(f"玩家 {player_id} 状态更新: {state_data}")
    
    def get_player_state(self, player_id):
        """获取玩家状态"""
        state = {
            'health': self.state_variables['player_health'].getValue(player_id, 20),
            'stamina': self.state_variables['player_stamina'].getValue(player_id, 100),
            'mana': self.state_variables['player_mana'].getValue(player_id, 50)
        }
        
        # 合并存储的状态
        if player_id in self.player_states:
            state.update(self.player_states[player_id])
        
        return state
    
    def apply_damage_to_player(self, player_id, damage_amount):
        """对玩家造成伤害"""
        current_health = self.state_variables['player_health'].getValue(player_id, 20)
        new_health = max(0, current_health - damage_amount)
        
        self.state_variables['player_health'].setValue(player_id, new_health)
        
        # 更新状态存储
        if player_id not in self.player_states:
            self.player_states[player_id] = {}
        
        self.player_states[player_id]['health'] = new_health
        
        print(f"玩家 {player_id} 受到伤害: {damage_amount}, 生命值: {current_health} -> {new_health}")
        
        # 检查玩家是否死亡
        if new_health <= 0:
            self.on_player_death(player_id)
        
        return new_health
    
    def on_player_death(self, player_id):
        """玩家死亡处理"""
        print(f"玩家 {player_id} 死亡")
        
        # 重置玩家状态
        self.reset_player_state(player_id)
        
        # 触发死亡事件
        self.trigger_death_event(player_id)
    
    def reset_player_state(self, player_id):
        """重置玩家状态"""
        default_state = {
            'health': 20,
            'stamina': 100,
            'mana': 50
        }
        
        self.update_player_state(player_id, default_state)
        print(f"玩家 {player_id} 状态已重置")
    
    def trigger_death_event(self, player_id):
        """触发死亡事件"""
        # 这里可以添加死亡特效、声音等
        print(f"触发玩家 {player_id} 死亡事件")
    
    def update_quest_progress(self, progress_value):
        """更新任务进度"""
        self.state_variables['quest_progress'].setValue(0, progress_value)
        print(f"更新任务进度: {progress_value}")
        
        # 检查任务完成
        if progress_value >= 100:
            self.on_quest_complete()
    
    def on_quest_complete(self):
        """任务完成处理"""
        print("任务完成!")
        
        # 奖励玩家
        self.reward_players()
    
    def reward_players(self):
        """奖励所有玩家"""
        for player_id in self.player_states.keys():
            # 增加玩家经验或物品
            print(f"奖励玩家 {player_id}")
    
    def set_weather_intensity(self, intensity):
        """设置天气强度"""
        self.state_variables['weather_intensity'].setValue(0, intensity)
        print(f"设置天气强度: {intensity}")
        
        # 根据强度调整游戏效果
        if intensity > 0.7:
            self.enable_storm_effects()
        elif intensity > 0.3:
            self.enable_rain_effects()
        else:
            self.enable_clear_weather()
    
    def enable_storm_effects(self):
        """启用风暴效果"""
        print("启用风暴效果")
        # 这里可以设置粒子效果、声音、光照等
    
    def enable_rain_effects(self):
        """启用下雨效果"""
        print("启用下雨效果")
    
    def enable_clear_weather(self):
        """启用晴朗天气"""
        print("启用晴朗天气")
    
    def get_game_summary(self):
        """获取游戏摘要"""
        summary = {
            'game_time': self.get_game_time(),
            'game_difficulty': self.get_game_difficulty(),
            'weather_intensity': self.state_variables['weather_intensity'].getValue(0, 0),
            'quest_progress': self.state_variables['quest_progress'].getValue(0, 0),
            'level_completion': self.state_variables['level_completion'].getValue(0, 0),
            'player_count': len(self.player_states),
            'players': {}
        }
        
        for player_id in self.player_states.keys():
            summary['players'][player_id] = self.get_player_state(player_id)
        
        return summary
```

### 3. 跨环境MoLang工具

```python
from ..architect.utils.molang.common import NamedVariable
from ...basic import isServer

class CrossEnvironmentMoLang:
    def __init__(self):
        self.variables = {}
        self.environment = 'server' if isServer() else 'client'
        
        print(f"初始化跨环境MoLang工具 (环境: {self.environment})")
    
    def create_environment_aware_variable(self, name):
        """创建环境感知变量"""
        variable = NamedVariable(name)
        self.variables[name] = variable
        
        print(f"创建环境感知变量: {name} (环境: {self.environment})")
        return variable
    
    def sync_variable_across_environments(self, actor_id, var_name, value):
        """跨环境同步变量"""
        # 设置本地变量
        if var_name not in self.variables:
            self.create_environment_aware_variable(var_name)
        
        self.variables[var_name].setValue(actor_id, value)
        
        # 根据环境决定是否同步
        if self.environment == 'client':
            # 客户端发送到服务器
            self.send_to_server(actor_id, var_name, value)
        else:
            # 服务器广播到所有客户端
            self.broadcast_to_clients(actor_id, var_name, value)
        
        print(f"同步变量 {var_name} = {value} (环境: {self.environment}, 实体: {actor_id})")
    
    def send_to_server(self, actor_id, var_name, value):
        """发送到服务器（客户端调用）"""
        # 这里应该实现网络通信
        print(f"[客户端] 发送变量到服务器: {var_name} = {value}")
    
    def broadcast_to_clients(self, actor_id, var_name, value):
        """广播到所有客户端（服务器调用）"""
        # 这里应该实现网络广播
        print(f"[服务器] 广播变量到客户端: {var_name} = {value}")
    
    def handle_sync_request(self, actor_id, var_name, value, source_environment):
        """处理同步请求"""
        print(f"收到同步请求: {var_name} = {value} (来源: {source_environment})")
        
        # 更新本地变量
        self.sync_variable_across_environments(actor_id, var_name, value)
    
    def create_shared_game_state(self):
        """创建共享游戏状态"""
        shared_vars = [
            'game_score',
            'game_time_remaining',
            'team_score_red',
            'team_score_blue',
            'game_phase'
        ]
        
        for var_name in shared_vars:
            self.create_environment_aware_variable(var_name)
        
        print(f"创建共享游戏状态变量: {shared_vars}")
        return shared_vars
    
    def update_shared_state(self, state_updates):
        """更新共享状态"""
        # 假设 actor_id 0 表示全局状态
        for var_name, value in state_updates.items():
            if var_name in self.variables:
                self.sync_variable_across_environments(0, var_name, value)
        
        print(f"更新共享状态: {state_updates}")
    
    def get_shared_state(self):
        """获取共享状态"""
        state = {}
        
        for var_name, variable in self.variables.items():
            # 假设 actor_id 0 表示全局状态
            value = variable.getValue(0, 0)
            state[var_name] = value
        
        return state
    
    def create_player_specific_variable(self, player_id, var_name):
        """创建玩家特定变量"""
        full_name = f"player_{player_id}_{var_name}"
        variable = self.create_environment_aware_variable(full_name)
        
        return variable
    
    def update_player_variable(self, player_id, var_name, value):
        """更新玩家变量"""
        full_name = f"player_{player_id}_{var_name}"
        
        if full_name not in self.variables:
            self.create_player_specific_variable(player_id, var_name)
        
        self.sync_variable_across_environments(player_id