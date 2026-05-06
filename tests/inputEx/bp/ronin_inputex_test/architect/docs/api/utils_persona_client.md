# 客户端角色系统 (PersonaClient) API

`architect.utils.persona.client` 模块提供了客户端角色渲染和外观管理功能，包括玩家和实体的材质、模型、动画、渲染控制器等渲染配置的动态修改。

## 依赖

- `...subsystem.ClientSubsystem` - 客户端子系统
- `...subsystem.SubsystemClient` - 客户端子系统装饰器
- `...component.Component` - 组件装饰器
- `...component.createComponent` - 创建组件
- `...component.getOneComponent` - 获取组件
- `...basic.compClient` - 客户端组件
- `...basic.clientApi` - 客户端API
- `...event.EventListener` - 事件监听器
- `mod.common.minecraftEnum.EntityType` - Minecraft实体类型枚举

## 常量

### `PlayerDefaultClientDef`

玩家默认客户端定义，包含完整的渲染配置：

- **`materials`**: 材质定义
  - `default`: "entity_alphatest"
  - `cape`: "entity_alphatest"
  - `animated`: "player_animated"
  - `spectator`: "player_spectator"
- **`textures`**: 贴图定义
  - `default`: "textures/entity/steve"
  - `cape`: "textures/entity/cape_invisible"
- **`geometry`**: 模型定义
  - `default`: "geometry.humanoid.custom"
  - `cape`: "geometry.cape"
- **`animations`**: 动画定义（包含83个动画和动画控制器）
- **`render_controllers`**: 渲染控制器定义（5个控制器）
- **`scripts`**: 脚本定义
  - `animate`: ["root"]

### `RenderConfKeys`

渲染配置键元组：
- `'geometry'`
- `'textures'`
- `'materials'`
- `'particle_effects'`
- `'animations'`
- `'render_controllers'`
- `'scripts'`

### `PlayerActorTypes`

玩家实体类型元组：
- `'minecraft:player'`
- `'player'`

## 组件类

### `PersonaRendererComponent`

角色渲染器组件，继承自 `BaseCompClient`，提供实体渲染配置管理。

#### 类属性

##### `_PlayerPrefabs`

静态列表，存储玩家类型渲染配置。

#### 构造函数

```python
def onCreate(self, entityId):
```

- **`entityId`**: 实体ID
- **初始化**:
  - `self.entityId`: 实体ID
  - `self.actorRenderer`: 创建ActorRender组件
  - `self.override`: 覆盖配置（默认None）
  - `self.playerPreloads`: 玩家预加载集合
  - `self.modified`: 是否已修改（默认False）
  - `self.molang`: 创建MoLang查询变量
  - `self.shadowRoot`: 阴影根动画（默认None）
  - 如果是玩家实体，调用 `_applyPlayerRenderConfToSelf()`

#### 方法

##### `broadcastRenderConf(jsonObj={})`

广播渲染配置到服务器。

- **`jsonObj`**: JSON配置对象
- **发送事件**: 'BroadcastPersonaChange' 到服务器

##### `broadcastResetConf()`

广播重置配置到服务器。

- **发送事件**: 'BroadcastPersonaReset' 到服务器

##### `addActorRenderConf(jsonObject, actor=None)`

为单个实体添加渲染配置。

- **`jsonObject`**: 配置JSON对象
- **`actor`**: 实体ID（可选，默认使用当前实体）
- **支持配置**:
  - `materials`: 材质
  - `geometry`: 模型
  - `textures`: 贴图
  - `animations`: 动画/动画控制器
  - `particle_effects`: 粒子效果
  - `sound_effects`: 音效
  - `render_controllers`: 渲染控制器
  - `scripts`: 脚本

##### `@staticmethod addActorTypeRenderConf(actorType, jsonObject)`

为实体类型添加渲染配置。

- **`actorType`**: 实体类型字符串
- **`jsonObject`**: 配置JSON对象

##### `hasRenderController(name)`

检查是否具有指定的渲染控制器。

- **`name`**: 渲染控制器名称
- **返回值**: 布尔值

##### `addPlayerRenderConf(jsonObject, rebuild=True)`

为玩家添加渲染配置。

- **`jsonObject`**: 配置JSON对象
- **`rebuild`**: 是否重建渲染（默认True）

##### `@staticmethod addPlayerTypeRenderConf(jsonObject)`

添加玩家类型渲染配置（静态方法）。

- **`jsonObject`**: 配置JSON对象
- **存储**: 添加到 `_PlayerPrefabs` 列表

##### `_applyPlayerRenderConfToSelf()`

应用玩家渲染配置到自身（内部方法）。

##### `rebuildRender()`

重建渲染。

##### `changeActorRenderConf(jsonObject, actor=None, full=False, broadcast=True)`

修改单个实体的渲染配置。

- **`jsonObject`**: 配置JSON对象
- **`actor`**: 实体ID（可选）
- **`full`**: 是否完整修改（包括geometry/texture/particle_effects）
- **`broadcast`**: 是否广播（默认True）

##### `changePlayerRenderConf(jsonObject={}, full=False, broadcast=True)`

修改玩家渲染配置。

- **`jsonObject`**: 配置JSON对象
- **`full`**: 是否完整修改
- **`broadcast`**: 是否广播（默认True）

##### `showHand(visible=True, mode=0)`

显示/隐藏玩家手中的物品。

- **`visible`**: 是否可见（默认True）
- **`mode`**: 模式（默认0）

##### `changeRenderConf(jsonObject, broadcast=True, full=False)`

修改渲染配置（自动判断玩家或实体）。

- **`jsonObject`**: 配置JSON对象
- **`broadcast`**: 是否广播（默认True）
- **`full`**: 是否完整修改（默认False）

##### `resetActorRenderConf(broadcast=True)`

重置单个实体的渲染配置。

- **`broadcast`**: 是否广播（默认True）

##### `resetPlayerRenderConf(broadcast=True, rebuild=True)`

重置玩家渲染配置。

- **`broadcast`**: 是否广播（默认True）
- **`rebuild`**: 是否重建渲染（默认True）

##### `resetRenderConf(broadcast=True, rebuild=True)`

重置渲染配置（自动判断玩家或实体）。

- **`broadcast`**: 是否广播（默认True）
- **`rebuild`**: 是否重建渲染（默认True）

##### `shadowPlayerRootAnim(anim=None)`

使用动画遮蔽玩家根动画。

- **`anim`**: 动画名称（可选）

##### `restorePlayerRootAnim()`

恢复玩家根动画。

## 工具函数

### `createPersona(id)`

创建角色渲染器组件。

- **`id`**: 实体ID
- **返回值**: `PersonaRendererComponent` 实例

### `getPersona(id)`

获取角色渲染器组件。

- **`id`**: 实体ID
- **返回值**: `PersonaRendererComponent` 实例或None

## 子系统类

### `PersonaEventsSubsystem`

角色事件子系统，继承自 `ClientSubsystem`。

#### 装饰器

`@SubsystemClient` - 标记为客户端子系统

#### 事件监听器

##### `onPersonaChangeServer(event)`

处理 'PersonaChangeServer' 自定义事件。

- **`event`**: 事件对象，包含 `id` 和 `data`
- **功能**: 修改指定实体的渲染配置

##### `onPersonaResetServer(event)`

处理 'PersonaResetServer' 自定义事件。

- **`event`**: 事件对象，包含 `id`
- **功能**: 重置指定实体的渲染配置

##### `onPersonaChangeClientAuthed(event)`

处理 'PersonaChangeClientAuthed' 自定义事件。

- **`event`**: 事件对象，包含 `id` 和 `data`
- **功能**: 修改指定实体的渲染配置（完整模式）

##### `onPersonaResetClientAuthed(event)`

处理 'PersonaResetClientAuthed' 自定义事件。

- **`event`**: 事件对象，包含 `id`
- **功能**: 重置指定实体的渲染配置

##### `onLocalPlayerStopLoading(_)`

处理 'OnLocalPlayerStopLoading' 事件。

- **功能**: 为本地玩家创建角色渲染器组件，并发送初始化事件到服务器

##### `onAddPlayerCreatedClientEvent(event)`

处理 'AddPlayerCreatedClientEvent' 事件。

- **`event`**: 事件对象，包含 `playerId`
- **功能**: 为其他玩家创建角色渲染器组件

## 使用示例

### 1. 基本角色渲染管理

```python
from ..architect.utils.persona.client import (
    createPersona, getPersona, PersonaRendererComponent,
    PersonaEventsSubsystem, PlayerDefaultClientDef
)

class CharacterCustomizer:
    def __init__(self):
        self.character_configs = {}
        self.setup_default_configs()
        
        # 获取子系统实例
        self.persona_subsystem = PersonaEventsSubsystem.getInstance()
    
    def setup_default_configs(self):
        """设置默认配置"""
        # 英雄配置
        self.character_configs['hero'] = {
            "materials": {
                "default": "entity_alphatest",
                "armor": "entity_armor_hero"
            },
            "textures": {
                "default": "textures/entity/hero/hero_default",
                "armor": "textures/entity/hero/hero_armor"
            },
            "geometry": {
                "default": "geometry.humanoid.hero",
                "cape": "geometry.cape.hero"
            },
            "animations": {
                "hero_walk": "animation.hero.walk",
                "hero_attack": "animation.hero.attack",
                "hero_idle": "animation.hero.idle"
            },
            "render_controllers": [
                {
                    "controller.render.hero": "!query.is_spectator"
                }
            ]
        }
        
        # 怪物配置
        self.character_configs['monster'] = {
            "materials": {
                "default": "entity_alphatest_monster"
            },
            "textures": {
                "default": "textures/entity/monster/zombie"
            },
            "geometry": {
                "default": "geometry.monster.zombie"
            },
            "animations": {
                "monster_walk": "animation.monster.walk",
                "monster_attack": "animation.monster.attack"
            }
        }
        
        print("角色配置设置完成")
    
    def customize_entity(self, entity_id, character_type):
        """自定义实体外观"""
        if character_type not in self.character_configs:
            print(f"未知角色类型: {character_type}")
            return False
        
        # 获取或创建角色渲染器
        persona = getPersona(entity_id)
        if not persona:
            persona = createPersona(entity_id)
        
        if not persona:
            print(f"无法为实体 {entity_id} 创建角色渲染器")
            return False
        
        # 应用配置
        config = self.character_configs[character_type]
        persona.changeRenderConf(config, broadcast=True)
        
        print(f"实体 {entity_id} 自定义为 {character_type}")
        return True
    
    def customize_player(self, player_id, character_type):
        """自定义玩家外观"""
        if character_type not in self.character_configs:
            print(f"未知角色类型: {character_type}")
            return False
        
        # 获取或创建角色渲染器
        persona = getPersona(player_id)
        if not persona:
            persona = createPersona(player_id)
        
        if not persona:
            print(f"无法为玩家 {player_id} 创建角色渲染器")
            return False
        
        # 应用玩家特定配置
        config = self.character_configs[character_type]
        persona.changePlayerRenderConf(config, broadcast=True)
        
        print(f"玩家 {player_id} 自定义为 {character_type}")
        return True
    
    def reset_entity_appearance(self, entity_id):
        """重置实体外观"""
        persona = getPersona(entity_id)
        if not persona:
            print(f"实体 {entity_id} 没有角色渲染器")
            return False
        
        persona.resetRenderConf(broadcast=True)
        print(f"实体 {entity_id} 外观已重置")
        return True
    
    def reset_player_appearance(self, player_id):
        """重置玩家外观"""
        persona = getPersona(player_id)
        if not persona:
            print(f"玩家 {player_id} 没有角色渲染器")
            return False
        
        persona.resetPlayerRenderConf(broadcast=True)
        print(f"玩家 {player_id} 外观已重置")
        return True
    
    def add_custom_animation(self, entity_id, animation_name, animation_path):
        """添加自定义动画"""
        persona = getPersona(entity_id)
        if not persona:
            print(f"实体 {entity_id} 没有角色渲染器")
            return False
        
        # 创建动画配置
        anim_config = {
            "animations": {
                animation_name: animation_path
            }
        }
        
        persona.changeRenderConf(anim_config, broadcast=True)
        print(f"为实体 {entity_id} 添加动画: {animation_name}")
        return True
    
    def add_custom_texture(self, entity_id, texture_name, texture_path):
        """添加自定义贴图"""
        persona = getPersona(entity_id)
        if not persona:
            print(f"实体 {entity_id} 没有角色渲染器")
            return False
        
        # 创建贴图配置（需要完整模式）
        texture_config = {
            "textures": {
                texture_name: texture_path
            }
        }
        
        persona.changeRenderConf(texture_config, broadcast=True, full=True)
        print(f"为实体 {entity_id} 添加贴图: {texture_name}")
        return True
    
    def add_particle_effect(self, entity_id, effect_name, effect_path):
        """添加粒子效果"""
        persona = getPersona(entity_id)
        if not persona:
            print(f"实体 {entity_id} 没有角色渲染器")
            return False
        
        # 创建粒子效果配置（需要完整模式）
        particle_config = {
            "particle_effects": {
                effect_name: effect_path
            }
        }
        
        persona.changeRenderConf(particle_config, broadcast=True, full=True)
        print(f"为实体 {entity_id} 添加粒子效果: {effect_name}")
        return True
    
    def show_entity_hand(self, entity_id, visible=True):
        """显示/隐藏实体手中的物品"""
        persona = getPersona(entity_id)
        if not persona:
            print(f"实体 {entity_id} 没有角色渲染器")
            return False
        
        # 检查是否是玩家
        from mod.common.minecraftEnum import EntityType
        from ...basic import compClient
        
        engine_type = compClient.CreateEngineType(entity_id).GetEngineType()
        if engine_type == EntityType.Player:
            persona.showHand(visible)
            print(f"设置玩家 {entity_id} 手中物品可见性: {visible}")
            return True
        else:
            print(f"实体 {entity_id} 不是玩家，无法设置手中物品")
            return False
    
    def create_character_preset(self, preset_name, config_data):
        """创建角色预设"""
        self.character_configs[preset_name] = config_data
        print(f"创建角色预设: {preset_name}")
        return True
    
    def apply_preset_to_all_players(self, preset_name):
        """将预设应用到所有玩家"""
        if preset_name not in self.character_configs:
            print(f"预设不存在: {preset_name}")
            return False
        
        config = self.character_configs[preset_name]
        
        # 这里需要获取所有玩家ID
        # 实际实现中可能需要从游戏API获取
        
        print(f"将预设 {preset_name} 应用到所有玩家")
        return True
    
    def batch_customize_entities(self, entity_ids, character_type):
        """批量自定义实体"""
        results = []
        
        for entity_id in entity_ids:
            success = self.customize_entity(entity_id, character_type)
            results.append((entity_id, success))
        
        success_count = sum(1 for _, success in results if success)
        print(f"批量自定义完成: {success_count}/{len(entity_ids)} 成功")
        return results
```

### 2. 高级角色变换系统

```python
from ..architect.utils.persona.client import (
    PersonaRendererComponent, createPersona, getPersona,
    PersonaEventsSubsystem
)

class AdvancedPersonaSystem:
    def __init__(self):
        self.transformations = {}
        self.active_transforms = {}
        self.transform_history = {}
        
        self.setup_transformation_templates()
        
        # 获取子系统
        self.persona_subsystem = PersonaEventsSubsystem.getInstance()
    
    def setup_transformation_templates(self):
        """设置变换模板"""
        # 变身模板
        self.transformations['werewolf'] = {
            "name": "狼人",
            "config": {
                "materials": {
                    "default": "entity_alphatest_werewolf",
                    "fur": "entity_fur_werewolf"
                },
                "textures": {
                    "default": "textures/entity/werewolf/werewolf_default",
                    "fur": "textures/entity/werewolf/werewolf_fur"
                },
                "geometry": {
                    "default": "geometry.werewolf",
                    "head": "geometry.werewolf.head"
                },
                "animations": {
                    "werewolf_walk": "animation.werewolf.walk",
                    "werewolf_run": "animation.werewolf.run",
                    "werewolf_howl": "animation.werewolf.howl",
                    "werewolf_attack": "animation.werewolf.attack"
                },
                "particle_effects": {
                    "trans