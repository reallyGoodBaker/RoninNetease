# 服务端角色系统 (PersonaServer) API

`architect.utils.persona.server` 模块提供了服务端角色渲染配置的同步和广播功能，用于在服务器端管理角色外观变化并同步到所有客户端。

## 依赖

- `...subsystem.ServerSubsystem` - 服务端子系统
- `...subsystem.SubsystemServer` - 服务端子系统装饰器
- `...event.EventListener` - 事件监听器
- `...basic.serverApi` - 服务端API
- `..enhance.list.remove` - 列表移除工具函数

## 子系统类

### `PersonaServer`

角色服务端子系统，继承自 `ServerSubsystem`，负责角色渲染配置的服务器端管理和同步。

#### 装饰器

`@SubsystemServer` - 标记为服务端子系统

#### 类属性

##### `_PersonaChanged`

静态字典，存储已修改的角色配置。
- **键**: 实体ID
- **值**: 渲染配置数据

#### 方法

##### `changePersona(id, renderConf)`

修改角色渲染配置并广播到所有客户端。

- **`id`**: 实体ID
- **`renderConf`**: 渲染配置对象
- **发送事件**: 'PersonaChangeServer' 到所有客户端

##### `resetPersona(id)`

重置角色渲染配置并广播到所有客户端。

- **`id`**: 实体ID
- **发送事件**: 'PersonaResetServer' 到所有客户端

#### 事件监听器

##### `onPersonaChangeClient(ev)`

处理 'BroadcastPersonaChange' 自定义事件（来自客户端）。

- **`ev`**: 事件对象，包含 `id` 和 `data`
- **功能**:
  1. 将配置存储到 `_PersonaChanged` 字典
  2. 获取玩家列表，移除事件发起者
  3. 向其他玩家发送 'PersonaChangeClientAuthed' 事件

##### `onPersonaResetClient(ev)`

处理 'BroadcastPersonaReset' 自定义事件（来自客户端）。

- **`ev`**: 事件对象，包含 `id`
- **功能**:
  1. 从 `_PersonaChanged` 字典中移除配置
  2. 获取玩家列表，移除事件发起者
  3. 向其他玩家发送 'PersonaResetClientAuthed' 事件

##### `onPersonaChangeClientInit(ev)`

处理 'PersonaChangeClientInit' 自定义事件（客户端初始化）。

- **`ev`**: 事件对象，包含 `__id__`（发起者ID）
- **功能**: 向新连接的客户端同步所有已修改的角色配置

## 使用示例

### 1. 基本角色同步管理

```python
from ..architect.utils.persona.server import PersonaServer

class ServerPersonaManager:
    def __init__(self):
        self.persona_server = PersonaServer.getInstance()
        self.character_registry = {}
        self.player_characters = {}
        
        self.setup_character_templates()
    
    def setup_character_templates(self):
        """设置角色模板"""
        self.character_registry['knight'] = {
            "name": "骑士",
            "config": {
                "materials": {
                    "armor": "entity_armor_knight"
                },
                "textures": {
                    "armor": "textures/entity/knight/armor"
                },
                "geometry": {
                    "armor": "geometry.knight.armor"
                },
                "animations": {
                    "knight_walk": "animation.knight.walk",
                    "knight_attack": "animation.knight.attack"
                }
            }
        }
        
        self.character_registry['mage'] = {
            "name": "法师",
            "config": {
                "materials": {
                    "robe": "entity_robe_mage"
                },
                "textures": {
                    "robe": "textures/entity/mage/robe"
                },
                "geometry": {
                    "robe": "geometry.mage.robe"
                },
                "animations": {
                    "mage_cast": "animation.mage.cast",
                    "mage_idle": "animation.mage.idle"
                },
                "particle_effects": {
                    "magic_aura": "particle.magic.aura"
                }
            }
        }
        
        self.character_registry['rogue'] = {
            "name": "盗贼",
            "config": {
                "materials": {
                    "cloak": "entity_cloak_rogue"
                },
                "textures": {
                    "cloak": "textures/entity/rogue/cloak"
                },
                "geometry": {
                    "cloak": "geometry.rogue.cloak"
                },
                "animations": {
                    "rogue_sneak": "animation.rogue.sneak",
                    "rogue_backstab": "animation.rogue.backstab"
                }
            }
        }
        
        print("角色模板设置完成")
    
    def assign_character_to_player(self, player_id, character_type):
        """为玩家分配角色"""
        if character_type not in self.character_registry:
            print(f"未知角色类型: {character_type}")
            return False
        
        character_config = self.character_registry[character_type]['config']
        
        # 记录玩家角色
        self.player_characters[player_id] = {
            'type': character_type,
            'config': character_config
        }
        
        # 通过服务器子系统广播到所有客户端
        if self.persona_server:
            self.persona_server.changePersona(player_id, character_config)
        
        print(f"为玩家 {player_id} 分配角色: {character_type}")
        return True
    
    def reset_player_character(self, player_id):
        """重置玩家角色"""
        if player_id not in self.player_characters:
            print(f"玩家 {player_id} 没有分配角色")
            return False
        
        # 从记录中移除
        del self.player_characters[player_id]
        
        # 通过服务器子系统广播重置
        if self.persona_server:
            self.persona_server.resetPersona(player_id)
        
        print(f"重置玩家 {player_id} 的角色")
        return True
    
    def change_player_character(self, player_id, new_character_type):
        """更改玩家角色"""
        if new_character_type not in self.character_registry:
            print(f"未知角色类型: {new_character_type}")
            return False
        
        # 分配新角色
        return self.assign_character_to_player(player_id, new_character_type)
    
    def get_player_character_info(self, player_id):
        """获取玩家角色信息"""
        if player_id not in self.player_characters:
            return None
        
        char_data = self.player_characters[player_id]
        char_type = char_data['type']
        
        if char_type in self.character_registry:
            return {
                'player_id': player_id,
                'character_type': char_type,
                'character_name': self.character_registry[char_type]['name'],
                'config': char_data['config']
            }
        
        return None
    
    def broadcast_character_to_all(self, character_type):
        """将角色广播给所有玩家"""
        if character_type not in self.character_registry:
            print(f"未知角色类型: {character_type}")
            return False
        
        character_config = self.character_registry[character_type]['config']
        
        # 获取所有玩家
        from ...basic import serverApi
        players = serverApi.GetPlayerList()
        
        if not players:
            print("没有找到玩家")
            return False
        
        # 为每个玩家分配角色
        for player_id in players:
            self.assign_character_to_player(player_id, character_type)
        
        print(f"为所有玩家分配角色: {character_type}")
        return True
    
    def handle_player_join(self, player_id):
        """处理玩家加入"""
        print(f"玩家 {player_id} 加入游戏")
        
        # 这里可以设置默认角色或恢复之前的状态
        # 例如：self.assign_character_to_player(player_id, 'default')
        
        return True
    
    def handle_player_leave(self, player_id):
        """处理玩家离开"""
        print(f"玩家 {player_id} 离开游戏")
        
        # 清理玩家数据
        if player_id in self.player_characters:
            del self.player_characters[player_id]
        
        return True
    
    def create_custom_character(self, character_name, config_data):
        """创建自定义角色"""
        if character_name in self.character_registry:
            print(f"角色 {character_name} 已存在")
            return False
        
        self.character_registry[character_name] = {
            "name": character_name,
            "config": config_data
        }
        
        print(f"创建自定义角色: {character_name}")
        return True
    
    def update_character_config(self, character_type, config_updates):
        """更新角色配置"""
        if character_type not in self.character_registry:
            print(f"未知角色类型: {character_type}")
            return False
        
        # 更新配置
        current_config = self.character_registry[character_type]['config']
        
        # 深度合并配置
        def deep_update(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_update(target[key], value)
                else:
                    target[key] = value
        
        deep_update(current_config, config_updates)
        
        # 更新所有使用该角色的玩家
        updated_players = []
        for player_id, char_data in self.player_characters.items():
            if char_data['type'] == character_type:
                # 重新广播配置
                if self.persona_server:
                    self.persona_server.changePersona(player_id, current_config)
                updated_players.append(player_id)
        
        print(f"更新角色 {character_type} 配置，影响玩家: {updated_players}")
        return True
    
    def get_server_status(self):
        """获取服务器状态"""
        status = {
            'total_players': len(self.player_characters),
            'character_types': list(self.character_registry.keys()),
            'player_distribution': {},
            'modified_characters': len(PersonaServer._PersonaChanged) if hasattr(PersonaServer, '_PersonaChanged') else 0
        }
        
        # 统计角色分布
        for player_id, char_data in self.player_characters.items():
            char_type = char_data['type']
            if char_type not in status['player_distribution']:
                status['player_distribution'][char_type] = 0
            status['player_distribution'][char_type] += 1
        
        return status
```

### 2. 游戏角色系统

```python
from ..architect.utils.persona.server import PersonaServer
from ...basic import serverApi

class GameRoleSystem:
    def __init__(self):
        self.persona_server = PersonaServer.getInstance()
        self.game_roles = {}
        self.team_assignments = {}
        self.role_abilities = {}
        
        self.setup_game_roles()
    
    def setup_game_roles(self):
        """设置游戏角色"""
        # PvP游戏角色
        self.game_roles['tank'] = {
            "name": "坦克",
            "description": "高生命值，低伤害，吸引敌人火力",
            "config": {
                "materials": {
                    "armor": "entity_armor_tank"
                },
                "textures": {
                    "armor": "textures/entity/tank/armor"
                },
                "geometry": {
                    "armor": "geometry.tank.armor",
                    "shield": "geometry.tank.shield"
                },
                "animations": {
                    "tank_block": "animation.tank.block",
                    "tank_taunt": "animation.tank.taunt"
                },
                "particle_effects": {
                    "shield_effect": "particle.shield.effect"
                }
            },
            "stats": {
                "health_multiplier": 2.0,
                "damage_multiplier": 0.7,
                "speed_multiplier": 0.8
            }
        }
        
        self.game_roles['damage'] = {
            "name": "伤害输出",
            "description": "高伤害，低生命值，快速消灭敌人",
            "config": {
                "materials": {
                    "weapon": "entity_weapon_damage"
                },
                "textures": {
                    "weapon": "textures/entity/damage/weapon"
                },
                "geometry": {
                    "weapon": "geometry.damage.weapon"
                },
                "animations": {
                    "damage_attack": "animation.damage.attack",
                    "damage_combo": "animation.damage.combo"
                },
                "particle_effects": {
                    "damage_trail": "particle.damage.trail"
                }
            },
            "stats": {
                "health_multiplier": 0.8,
                "damage_multiplier": 1.5,
                "speed_multiplier": 1.1
            }
        }
        
        self.game_roles['support'] = {
            "name": "支援",
            "description": "治疗队友，提供增益效果",
            "config": {
                "materials": {
                    "robe": "entity_robe_support"
                },
                "textures": {
                    "robe": "textures/entity/support/robe"
                },
                "geometry": {
                    "staff": "geometry.support.staff"
                },
                "animations": {
                    "support_heal": "animation.support.heal",
                    "support_buff": "animation.support.buff"
                },
                "particle_effects": {
                    "heal_effect": "particle.heal.effect",
                    "buff_effect": "particle.buff.effect"
                }
            },
            "stats": {
                "health_multiplier": 1.0,
                "damage_multiplier": 0.9,
                "speed_multiplier": 1.0
            }
        }
        
        self.game_roles['assassin'] = {
            "name": "刺客",
            "description": "隐身，高爆发伤害，偷袭敌人",
            "config": {
                "materials": {
                    "cloak": "entity_cloak_assassin"
                },
                "textures": {
                    "cloak": "textures/entity/assassin/cloak"
                },
                "geometry": {
                    "dagger": "geometry.assassin.dagger"
                },
                "animations": {
                    "assassin_stealth": "animation.assassin.stealth",
                    "assassin_backstab": "animation.assassin.backstab"
                },
                "particle_effects": {
                    "stealth_effect": "particle.stealth.effect"
                }
            },
            "stats": {
                "health_multiplier": 0.7,
                "damage_multiplier": 1.8,
                "speed_multiplier": 1.2
            }
        }
        
        print("游戏角色设置完成")
    
    def assign_role_to_player(self, player_id, role_type):
        """为玩家分配游戏角色"""
        if role_type not in self.game_roles:
            print(f"未知角色类型: {role_type}")
            return False
        
        role_data = self.game_roles[role_type]
        
        # 记录玩家角色
        self.role_abilities[player_id] = {
            'role': role_type,
            'stats': role_data['stats'],
            'assigned_at': time.time()
        }
        
        # 应用角色外观配置
        if self.persona_server:
            self.persona_server.changePersona(player_id, role_data['config'])
        
        # 应用角色能力（这里需要与游戏系统集成）
        self.apply_role_abilities(player_id, role_data['stats'])
        
        print(f"为玩家 {player_id} 分配角色: {role_type} ({role_data['name']})")
        return True
    
    def apply_role_abilities(self, player_id, stats):
        """应用角色能力"""
        # 这里应该与游戏属性系统集成
        # 例如：设置玩家生命值、伤害、速度等
        
        print(f"为玩家 {player_id} 应用角色能力: {stats}")
        
        # 示例：设置玩家属性
        # from ...basic import serverApi
        # player_comp = serverApi.GetEngineCompFactory().CreateGame(player_id)
        # player_comp.SetAttr(...)
        
        return True
    
    def assign_teams(self, players_per_team=2):
        """分配队伍"""
        players = serverApi.GetPlayerList()
        
        if not players:
            print("没有找到玩家")
            return False
        
        # 随机打乱玩家顺序
        import random
        random.shuffle(players)
        
        # 分配队伍
        teams = {}
        team_colors = ['red', 'blue', 'green', 'yellow']
        
        for i, player_id in enumerate(players):
            team_index = i % len(team_colors)
            team_color = team_colors[team_index]
            
            if team_color not in teams:
                teams[team_color] = []
            
            teams[team_color].append(player_id)
            self.team_assignments[player_id] = team_color
        
        print(f"队伍分配完成: {teams}")
        return teams
    
    def assign_balanced_roles(self):
        """分配平衡的角色"""
        players = serverApi.GetPlayerList()
        
        if not players:
            print("没有找到玩家")
            return False
        
        # 可用的角色类型
        available_roles = list(self.game_roles.keys())
        
        # 确保每个角色类型至少有一个玩家
        import random
        random.shuffle(players)
        
        results = []
        
        for i, player_id in enumerate(players):
            # 循环使用角色类型
            role_type = available_roles[i % len(available_roles)]
            success = self.assign_role_to_player(player_id, role_type)
            results.append((player_id, role_type, success))
        
        success_count = sum(1 for _, _, success in results if success)
        print(f"