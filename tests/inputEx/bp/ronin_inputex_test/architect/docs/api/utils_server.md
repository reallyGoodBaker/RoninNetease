# 服务端工具 (ServerUtils) API

`architect.utils.server` 模块提供了服务端实用工具，包括命令执行、实体运动控制、音效播放和粒子效果等功能。

## 依赖

- `..level.server.LevelServer`, `compServer` - 服务端层级组件
- `mod.common.minecraftEnum.EntityType` - Minecraft实体类型枚举
- `..subsystem.ServerSubsystem`, `SubsystemServer` - 服务端子系统和装饰器

## 函数

### `runCommand(cmd, entityId)`

执行Minecraft命令。

- **`cmd`**: 要执行的命令字符串
- **`entityId`**: 执行命令的实体ID
- **返回值**: 命令执行结果

### `motion(entityId, mot, ignoreTypes=[])`

设置实体运动。

- **`entityId`**: 实体ID
- **`mot`**: 运动向量
- **`ignoreTypes`**: 忽略的实体类型列表
- **返回值**: 运动设置结果

### `sound(entityId, sound)`

播放声音效果。

- **`entityId`**: 实体ID
- **`sound`**: 声音标识符
- **返回值**: 命令执行结果

### `particle(particle, pos)`

创建粒子效果。

- **`particle`**: 粒子类型
- **`pos`**: 位置坐标 (x, y, z)
- **返回值**: 命令执行结果

### `soundServer(entityId, sound)`

通过服务端子系统播放声音。

- **`entityId`**: 实体ID
- **`sound`**: 声音标识符

### `soundStopServer(entityId, sound)`

通过服务端子系统停止声音。

- **`entityId`**: 实体ID
- **`sound`**: 声音标识符

## 类

### `ServerUtilsSubsys`

服务端工具子系统类，继承自 `ServerSubsystem`，使用 `@SubsystemServer` 装饰器标记。

#### 装饰器

##### `@SubsystemServer`

将类标记为服务端子系统，使其能够集成到架构的子系统管理器中。

#### 静态方法

##### `getInstance()`

获取子系统实例（类型提示中提到的静态方法）。

#### 方法

##### `playSound(entityId, sound)`

播放自定义音频。

- **`entityId`**: 实体ID
- **`sound`**: 声音标识符
- **功能**: 向所有客户端发送 `PlayCustomAudio` 事件

##### `stopSound(entityId, sound)`

停止自定义音频。

- **`entityId`**: 实体ID
- **`sound`**: 声音标识符
- **功能**: 向所有客户端发送 `StopCustomAudio` 事件

## 使用示例

### 1. 基本命令和效果

```python
from ..architect.utils.server import (
    runCommand, motion, sound, particle, 
    soundServer, soundStopServer, ServerUtilsSubsys
)
from ..architect.subsystem import SubsystemManager
from ..architect.math.vec3 import Vec3

class GameServerUtils:
    def __init__(self):
        # 获取服务端工具子系统实例
        self.server_utils = SubsystemManager.getInstance().getSubsystem(ServerUtilsSubsys)
    
    def teleport_player(self, player_id, position):
        """传送玩家到指定位置"""
        x, y, z = position
        command = f"tp {player_id} {x} {y} {z}"
        result = runCommand(command, player_id)
        
        if result:
            print(f"玩家 {player_id} 已传送到 {position}")
        else:
            print(f"传送玩家 {player_id} 失败")
        
        return result
    
    def give_item(self, player_id, item_id, amount=1):
        """给予玩家物品"""
        command = f"give {player_id} {item_id} {amount}"
        result = runCommand(command, player_id)
        
        if result:
            print(f"给予玩家 {player_id} {amount} 个 {item_id}")
        else:
            print(f"给予物品失败")
        
        return result
    
    def set_player_motion(self, player_id, motion_vector):
        """设置玩家运动"""
        # 忽略的实体类型（如果需要）
        ignore_types = []
        
        result = motion(player_id, motion_vector, ignore_types)
        
        if result:
            print(f"设置玩家 {player_id} 运动: {motion_vector}")
        else:
            print(f"设置玩家运动失败")
        
        return result
    
    def push_player(self, player_id, direction, force=1.0):
        """推动玩家"""
        # 创建运动向量
        motion_vector = Vec3(
            direction[0] * force,
            direction[1] * force,
            direction[2] * force
        )
        
        return self.set_player_motion(player_id, motion_vector)
    
    def play_sound_for_player(self, player_id, sound_id):
        """为玩家播放声音"""
        result = sound(player_id, sound_id)
        
        if result:
            print(f"为玩家 {player_id} 播放声音: {sound_id}")
        else:
            print(f"播放声音失败")
        
        return result
    
    def play_sound_for_all(self, sound_id):
        """为所有玩家播放声音"""
        # 使用服务端子系统播放声音（entityId=0表示全局）
        self.server_utils.playSound(0, sound_id)
        print(f"为所有玩家播放声音: {sound_id}")
    
    def stop_sound_for_all(self, sound_id):
        """为所有玩家停止声音"""
        # 使用服务端子系统停止声音
        self.server_utils.stopSound(0, sound_id)
        print(f"为所有玩家停止声音: {sound_id}")
    
    def create_particle_effect(self, particle_type, position, count=10):
        """创建粒子效果"""
        # 创建多个粒子
        x, y, z = position
        
        for i in range(count):
            # 添加随机偏移
            offset_x = x + (i * 0.1)
            offset_y = y + (i * 0.05)
            offset_z = z + (i * 0.1)
            
            result = particle(particle_type, (offset_x, offset_y, offset_z))
            
            if not result:
                print(f"创建粒子效果失败")
                break
        
        print(f"创建粒子效果: {particle_type} 在 {position}")
    
    def create_explosion_effect(self, position, power=4.0):
        """创建爆炸效果"""
        x, y, z = position
        
        # 播放爆炸声音
        self.play_sound_for_all("entity.generic.explode")
        
        # 创建爆炸粒子
        self.create_particle_effect("minecraft:huge_explosion_emitter", position)
        
        # 执行爆炸命令
        command = f"summon minecraft:tnt {x} {y} {z} {{Fuse:0}}"
        result = runCommand(command, 0)
        
        if result:
            print(f"创建爆炸效果在 {position}, 威力: {power}")
        else:
            print(f"创建爆炸效果失败")
        
        return result
    
    def create_heal_effect(self, player_id):
        """创建治疗效果"""
        # 获取玩家位置
        # 注意：这里需要实际获取玩家位置的方法
        player_pos = (0, 0, 0)  # 假设的位置
        
        # 播放治疗声音
        self.play_sound_for_player(player_id, "entity.player.levelup")
        
        # 创建治疗粒子
        self.create_particle_effect("minecraft:heart", player_pos, count=5)
        
        print(f"为玩家 {player_id} 创建治疗效果")
    
    def create_damage_effect(self, player_id):
        """创建伤害效果"""
        # 获取玩家位置
        player_pos = (0, 0, 0)  # 假设的位置
        
        # 播放伤害声音
        self.play_sound_for_player(player_id, "entity.player.hurt")
        
        # 创建伤害粒子
        self.create_particle_effect("minecraft:damage_indicator", player_pos, count=3)
        
        print(f"为玩家 {player_id} 创建伤害效果")
```

### 2. 游戏事件系统

```python
from ..architect.utils.server import ServerUtilsSubsys
from ..architect.subsystem import SubsystemManager
from ..architect.event import Event

class GameEventSystem(ServerUtilsSubsys):
    def __init__(self):
        super().__init__()
        self.game_events = {}
        self.event_listeners = {}
    
    def onInit(self):
        """初始化"""
        super().onInit()
        print("游戏事件系统已初始化")
        
        # 注册默认游戏事件
        self.register_default_events()
    
    def register_default_events(self):
        """注册默认游戏事件"""
        self.register_game_event("player_join", {
            "sound": "ui.toast.in",
            "particle": "minecraft:heart",
            "message": "玩家加入了游戏"
        })
        
        self.register_game_event("player_leave", {
            "sound": "ui.toast.out",
            "particle": "minecraft:smoke",
            "message": "玩家离开了游戏"
        })
        
        self.register_game_event("player_level_up", {
            "sound": "entity.player.levelup",
            "particle": "minecraft:enchanting_table_particles",
            "message": "玩家升级了!"
        })
        
        self.register_game_event("player_death", {
            "sound": "entity.player.death",
            "particle": "minecraft:explosion_emitter",
            "message": "玩家死亡了"
        })
        
        self.register_game_event("item_pickup", {
            "sound": "entity.item.pickup",
            "particle": "minecraft:item",
            "message": "拾取了物品"
        })
        
        self.register_game_event("boss_spawn", {
            "sound": "entity.enderdragon.growl",
            "particle": "minecraft:portal",
            "message": "Boss出现了!"
        })
        
        self.register_game_event("boss_defeat", {
            "sound": "entity.enderdragon.death",
            "particle": "minecraft:totem_of_undying",
            "message": "Boss被击败了!"
        })
    
    def register_game_event(self, event_name, event_config):
        """注册游戏事件"""
        self.game_events[event_name] = event_config
        print(f"注册游戏事件: {event_name}")
    
    def trigger_game_event(self, event_name, player_id=None, extra_data=None):
        """触发游戏事件"""
        if event_name not in self.game_events:
            print(f"错误: 未知游戏事件: {event_name}")
            return
        
        event_config = self.game_events[event_name]
        
        print(f"触发游戏事件: {event_name}")
        
        # 播放声音
        if "sound" in event_config:
            if player_id:
                self.playSound(player_id, event_config["sound"])
            else:
                self.playSound(0, event_config["sound"])
        
        # 创建粒子效果
        if "particle" in event_config and extra_data and "position" in extra_data:
            from ..architect.utils.server import particle
            particle(event_config["particle"], extra_data["position"])
        
        # 发送消息
        if "message" in event_config:
            message = event_config["message"]
            
            # 添加额外数据到消息
            if extra_data and "player_name" in extra_data:
                message = message.replace("玩家", extra_data["player_name"])
            
            # 发送消息给所有玩家
            self.send_message_to_all(message)
        
        # 触发事件监听器
        if event_name in self.event_listeners:
            for listener in self.event_listeners[event_name]:
                listener(player_id, extra_data)
    
    def send_message_to_all(self, message):
        """发送消息给所有玩家"""
        command = f'tellraw @a {{"text":"{message}","color":"yellow"}}'
        from ..architect.utils.server import runCommand
        runCommand(command, 0)
    
    def add_event_listener(self, event_name, listener):
        """添加事件监听器"""
        if event_name not in self.event_listeners:
            self.event_listeners[event_name] = []
        
        self.event_listeners[event_name].append(listener)
        print(f"添加事件监听器: {event_name}")
    
    def remove_event_listener(self, event_name, listener):
        """移除事件监听器"""
        if event_name in self.event_listeners and listener in self.event_listeners[event_name]:
            self.event_listeners[event_name].remove(listener)
            print(f"移除事件监听器: {event_name}")
    
    def on_player_join(self, player_id, player_name):
        """玩家加入事件"""
        extra_data = {
            "player_name": player_name,
            "position": self.get_player_position(player_id)
        }
        
        self.trigger_game_event("player_join", player_id, extra_data)
    
    def on_player_leave(self, player_id, player_name):
        """玩家离开事件"""
        extra_data = {
            "player_name": player_name
        }
        
        self.trigger_game_event("player_leave", player_id, extra_data)
    
    def on_player_level_up(self, player_id, player_name, new_level):
        """玩家升级事件"""
        extra_data = {
            "player_name": player_name,
            "level": new_level,
            "position": self.get_player_position(player_id)
        }
        
        self.trigger_game_event("player_level_up", player_id, extra_data)
    
    def on_player_death(self, player_id, player_name, killer_name=None):
        """玩家死亡事件"""
        extra_data = {
            "player_name": player_name,
            "killer_name": killer_name,
            "position": self.get_player_position(player_id)
        }
        
        self.trigger_game_event("player_death", player_id, extra_data)
    
    def on_item_pickup(self, player_id, player_name, item_name):
        """物品拾取事件"""
        extra_data = {
            "player_name": player_name,
            "item_name": item_name,
            "position": self.get_player_position(player_id)
        }
        
        self.trigger_game_event("item_pickup", player_id, extra_data)
    
    def on_boss_spawn(self, boss_name, position):
        """Boss出现事件"""
        extra_data = {
            "boss_name": boss_name,
            "position": position
        }
        
        self.trigger_game_event("boss_spawn", None, extra_data)
    
    def on_boss_defeat(self, boss_name, position, killer_name):
        """Boss击败事件"""
        extra_data = {
            "boss_name": boss_name,
            "position": position,
            "killer_name": killer_name
        }
        
        self.trigger_game_event("boss_defeat", None, extra_data)
    
    def get_player_position(self, player_id):
        """获取玩家位置（示例实现）"""
        # 这里需要实际获取玩家位置的方法
        # 返回假设的位置
        return (0, 0, 0)
```

### 3. 实体控制系统

```python
from ..architect.utils.server import motion, runCommand
from ..architect.math.vec3 import Vec3
import math

class EntityControlSystem:
    def __init__(self):
        self.controlled_entities = {}
        self.entity_behaviors = {}
    
    def control_entity(self, entity_id, control_type, params):
        """控制实体"""
        if control_type == "move_to":
            return self.move_entity_to(entity_id, params["target_position"], params.get("speed", 1.0))
        elif control_type == "follow":
            return self.follow_entity(entity_id, params["target_entity_id"], params.get("distance", 3.0))
        elif control_type == "wander":
            return self.wander_entity(entity_id, params.get("area_center"), params.get("radius", 10.0))
        elif control_type == "attack":
            return self.attack_entity(entity_id, params["target_entity_id"])
        elif control_type == "flee":
            return self.flee_entity(entity_id, params["threat_entity_id"], params.get("distance", 10.0))
        else:
            print(f"错误: 未知控制类型: {control_type}")
            return False
    
    def move_entity_to(self, entity_id, target_position, speed=1.0):
        """移动实体到指定位置"""
        # 获取实体当前位置
        current_position = self.get_entity_position(entity_id)
        if not current_position:
            return False
        
        # 计算方向向量
        direction = Vec3(
            target_position[0] - current_position[0],
            target_position[1] - current_position[1],
            target_position[2] - current_position[2]
        )
        
        # 归一化方向向量
        length = math.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
        if length > 0:
            direction.x /= length
            direction.y /= length
            direction.z /= length
        
        # 应用运动
        motion_vector = Vec3(
            direction.x * speed,
            direction.y * speed,
            direction.z * speed
        )
        
        result = motion(entity_id, motion_vector)
        
        if result:
            print(f"移动实体 {entity_id} 到 {target_position}, 速度: {speed}")
            
            # 检查是否到达目标
            distance = self.calculate_distance(current_position, target_position)
            if distance < 1.0:
                print(f"实体 {entity_id} 已到达目标位置")
                return True
        else:
            print(f"移动实体失败")
        
        return result
    
    def follow_entity(self, entity_id, target_entity_id, distance=3.0):
        """跟随目标实体"""
        # 获取目标实体位置
        target_position = self.get_entity_position(target_entity_id)
        if not target_position:
            return False
        
        # 获取当前实体位置
        current_position = self.get_entity_position(entity_id)
        if not current_position:
            return False
        
        # 计算当前