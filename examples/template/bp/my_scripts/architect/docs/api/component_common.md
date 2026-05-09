# 组件通用 (Component Common) API

`architect.component.common` 模块提供了网易引擎原生组件的访问函数和组件名称常量。

## `_nativeCompGet(entityId, name)` 函数

内部函数，用于获取网易引擎的原生组件实例。

### 参数

- **`entityId`**: (字符串) 实体 ID。
- **`name`**: (字符串) 组件名称（以 `#` 开头，例如 `#Pos`）。

### 返回值

- 返回对应的原生组件实例。

### 说明

- 根据当前运行环境（服务端或客户端）调用相应的引擎 API。
- 服务端使用 `compServer.Create{ComponentName}`，客户端使用 `compClient.Create{ComponentName}`。
- 此函数主要用于内部实现，不建议直接使用。

## `NeC` 类 (客户端组件名称)

`NeC` 类定义了客户端原生组件的名称常量。所有常量都以 `#` 开头。

### 常量列表

- `Achievement` = `'#Achievement'`
- `Action` = `'#Action'`
- `ActorMotion` = `'#ActorMotion'`
- `ActorRender` = `'#ActorRender'`
- `Attr` = `'#Attr'`
- `AuxValue` = `'#AuxValue'`
- `Biome` = `'#Biome'`
- `Block` = `'#Block'`
- `BlockGeometry` = `'#BlockGeometry'`
- `BlockInfo` = `'#BlockInfo'`
- `BlockUseEventWhiteList` = `'#BlockUseEventWhiteList'`
- `Brightness` = `'#Brightness'`
- `Camera` = `'#Camera'`
- `ChunkSource` = `'#ChunkSource'`
- `CollisionBox` = `'#CollisionBox'`
- `ConfigClient` = `'#ConfigClient'`
- `CustomAudio` = `'#CustomAudio'`
- `Device` = `'#Device'`
- `Dimension` = `'#Dimension'`
- `Drawing` = `'#Drawing'`
- `Effect` = `'#Effect'`
- `EngineEffectBindControl` = `'#EngineEffectBindControl'`
- `EngineType` = `'#EngineType'`
- `Fog` = `'#Fog'`
- `FrameAniControl` = `'#FrameAniControl'`
- `FrameAniEntityBind` = `'#FrameAniEntityBind'`
- `FrameAniSkeletonBind` = `'#FrameAniSkeletonBind'`
- `FrameAniTrans` = `'#FrameAniTrans'`
- `Game` = `'#Game'`
- `Health` = `'#Health'`
- `Item` = `'#Item'`
- `ModAttr` = `'#ModAttr'`
- `Model` = `'#Model'`
- `Name` = `'#Name'`
- `NeteaseShop` = `'#NeteaseShop'`
- `NeteaseWindow` = `'#NeteaseWindow'`
- `Operation` = `'#Operation'`
- `ParticleControl` = `'#ParticleControl'`
- `ParticleEntityBind` = `'#ParticleEntityBind'`
- `ParticleSkeletonBind` = `'#ParticleSkeletonBind'`
- `ParticleSystem` = `'#ParticleSystem'`
- `ParticleTrans` = `'#ParticleTrans'`
- `Player` = `'#Player'`
- `PlayerAnim` = `'#PlayerAnim'`
- `PlayerView` = `'#PlayerView'`
- `Pos` = `'#Pos'`
- `PostProcess` = `'#PostProcess'`
- `QueryVariable` = `'#QueryVariable'`
- `Recipe` = `'#Recipe'`
- `Ride` = `'#Ride'`
- `Rot` = `'#Rot'`
- `SkyRender` = `'#SkyRender'`
- `Tame` = `'#Tame'`
- `TextBoard` = `'#TextBoard'`
- `TextNotifyClient` = `'#TextNotifyClient'`
- `Time` = `'#Time'`
- `VirtualWorld` = `'#VirtualWorld'`

## `NeS` 类 (服务端组件名称)

`NeS` 类定义了服务端原生组件的名称常量。所有常量都以 `#` 开头。

### 常量列表

- `Achievement` = `'#Achievement'`
- `Action` = `'#Action'`
- `ActorCollidable` = `'#ActorCollidable'`
- `ActorLoot` = `'#ActorLoot'`
- `ActorMotion` = `'#ActorMotion'`
- `ActorOwner` = `'#ActorOwner'`
- `ActorPushable` = `'#ActorPushable'`
- `AiCommand` = `'#AiCommand'`
- `Attr` = `'#Attr'`
- `AuxValue` = `'#AuxValue'`
- `Biome` = `'#Biome'`
- `Block` = `'#Block'`
- `BlockEntity` = `'#BlockEntity'`
- `BlockEntityData` = `'#BlockEntityData'`
- `BlockInfo` = `'#BlockInfo'`
- `BlockState` = `'#BlockState'`
- `BlockUseEventWhiteList` = `'#BlockUseEventWhiteList'`
- `Breath` = `'#Breath'`
- `BulletAttributes` = `'#BulletAttributes'`
- `ChatExtension` = `'#ChatExtension'`
- `ChestBlock` = `'#ChestBlock'`
- `ChunkSource` = `'#ChunkSource'`
- `CollisionBox` = `'#CollisionBox'`
- `Command` = `'#Command'`
- `ControlAi` = `'#ControlAi'`
- `Dimension` = `'#Dimension'`
- `Effect` = `'#Effect'`
- `EngineType` = `'#EngineType'`
- `EntityComponent` = `'#EntityComponent'`
- `EntityDefinitions` = `'#EntityDefinitions'`
- `EntityEvent` = `'#EntityEvent'`
- `Exp` = `'#Exp'`
- `Explosion` = `'#Explosion'`
- `ExtraData` = `'#ExtraData'`
- `Feature` = `'#Feature'`
- `Fly` = `'#Fly'`
- `Game` = `'#Game'`
- `Gravity` = `'#Gravity'`
- `Http` = `'#Http'`
- `Hurt` = `'#Hurt'`
- `Interact` = `'#Interact'`
- `Item` = `'#Item'`
- `ItemBanned` = `'#ItemBanned'`
- `Loot` = `'#Loot'`
- `Lv` = `'#Lv'`
- `MobSpawn` = `'#MobSpawn'`
- `ModAttr` = `'#ModAttr'`
- `Model` = `'#Model'`
- `MoveTo` = `'#MoveTo'`
- `Msg` = `'#Msg'`
- `Name` = `'#Name'`
- `Persistence` = `'#Persistence'`
- `Pet` = `'#Pet'`
- `Physx` = `'#Physx'`
- `Player` = `'#Player'`
- `Portal` = `'#Portal'`
- `Pos` = `'#Pos'`
- `Projectile` = `'#Projectile'`
- `QueryVariable` = `'#QueryVariable'`
- `Recipe` = `'#Recipe'`
- `RedStone` = `'#RedStone'`
- `Ride` = `'#Ride'`
- `Rot` = `'#Rot'`
- `Scale` = `'#Scale'`
- `Shareables` = `'#Shareables'`
- `Tag` = `'#Tag'`
- `Tame` = `'#Tame'`
- `Time` = `'#Time'`
- `Weather` = `'#Weather'`

## 使用示例

```python
from ..architect.component.common import NeC, NeS

# 使用客户端组件名称
pos_comp_name = NeC.Pos  # '#Pos'

# 使用服务端组件名称
attr_comp_name = NeS.Attr  # '#Attr'
```
