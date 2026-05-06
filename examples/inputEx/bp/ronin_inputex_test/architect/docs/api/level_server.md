# 服务端关卡 (Level Server) API

`architect.level.server` 模块提供了服务端关卡功能，封装了 Minecraft 服务端 API 的关卡相关组件。

## `LevelServer` 类

`LevelServer` 类是服务端关卡的静态类，提供了对服务端关卡组件的便捷访问。所有组件都是类属性，可以直接通过类名访问。

### 类属性

#### `game`

- **类型**: `GameServer`
- **说明**: 游戏组件。

#### `chunkSource`

- **类型**: `ChunkSourceServer`
- **说明**: 区块源组件。

#### `achievement`

- **类型**: `AchievementServer`
- **说明**: 成就组件。

#### `biome`

- **类型**: `BiomeServer`
- **说明**: 生物群系组件。

#### `dimension`

- **类型**: `DimensionServer`
- **说明**: 维度组件。

#### `blockInfo`

- **类型**: `BlockInfoServer`
- **说明**: 方块信息组件。

#### `weather`

- **类型**: `WeatherServer`
- **说明**: 天气组件。

#### `time`

- **类型**: `TimeServer`
- **说明**: 时间组件。

#### `block`

- **类型**: `BlockServer`
- **说明**: 方块组件。

#### `blockEntity`

- **类型**: `BlockEntityServer`
- **说明**: 方块实体组件。

#### `blockEntityData`

- **类型**: `BlockEntityDataServer`
- **说明**: 方块实体数据组件。

#### `blockState`

- **类型**: `BlockStateServer`
- **说明**: 方块状态组件。

#### `blockUseEventWhiteList`

- **类型**: `BlockUseEventWhiteListServer`
- **说明**: 方块使用事件白名单组件。

#### `message`

- **类型**: `MsgServer`
- **说明**: 消息组件。

#### `command`

- **类型**: `CommandServer`
- **说明**: 命令组件。

#### `chestBlock`

- **类型**: `ChestBlockServer`
- **说明**: 箱子方块组件。

#### `explosion`

- **类型**: `ExplosionServer`
- **说明**: 爆炸组件。

#### `extraData`

- **类型**: `ExtraDataServer`
- **说明**: 额外数据组件。

#### `feature`

- **类型**: `FeatureServer`
- **说明**: 特征组件。

#### `itemBanned`

- **类型**: `ItemBannedServer`
- **说明**: 禁用物品组件。

#### `mobSpawn`

- **类型**: `MobSpawnServer`
- **说明**: 生物生成组件。

#### `projectile`

- **类型**: `ProjectileServer`
- **说明**: 抛射物组件。

#### `portal`

- **类型**: `PortalServer`
- **说明**: 传送门组件。

#### `recipe`

- **类型**: `RecipeServer`
- **说明**: 配方组件。

#### `redstone`

- **类型**: `RedStoneServer`
- **说明**: 红石组件。

## 使用示例

### 1. 直接访问组件

```python
from ..architect.level.server import LevelServer

# 使用命令组件执行命令
LevelServer.command.SetCommand('time set day')

# 使用消息组件发送消息
LevelServer.message.NotifyOneMessage('player_123', 'Welcome to the server!', '§a')

# 使用时间组件获取当前时间
current_time = LevelServer.time.GetTime()
print(f'当前时间: {current_time}')

# 使用天气组件设置天气
LevelServer.weather.SetWeather('clear', 10000)  # 晴天，持续10000刻
```

### 2. 世界操作

```python
from ..architect.level.server import LevelServer

# 获取方块信息
block_info = LevelServer.blockInfo.GetBlock((0, 64, 0), 0)
print(f'方块信息: {block_info}')

# 设置方块
LevelServer.block.SetBlock((10, 64, 10), 'minecraft:diamond_block', 0)

# 生成生物
LevelServer.mobSpawn.SpawnMob('minecraft:creeper', (20, 64, 20), 0)

# 创建爆炸
LevelServer.explosion.CreateExplosion((30, 64, 30), 5.0, True, True)
```

### 3. 游戏管理

```python
from ..architect.level.server import LevelServer

# 获取游戏规则
game_rule = LevelServer.game.GetGameRule('doDaylightCycle')
print(f'昼夜循环规则: {game_rule}')

# 设置游戏规则
LevelServer.game.SetGameRule('keepInventory', True)

# 添加配方
recipe_dict = {
    'type': 'crafting_shaped',
    'pattern': ['AAA', ' A ', 'AAA'],
    'key': {'A': {'item': 'minecraft:stone'}},
    'result': {'item': 'minecraft:stone_bricks', 'count': 8}
}
LevelServer.recipe.AddRecipe('custom_recipe', recipe_dict)
```

## 注意事项

1. **静态类**: `LevelServer` 是静态类，所有组件都是类属性，无需实例化。
2. **服务端专用**: 该模块仅用于服务端环境，客户端应使用 `architect.level.client` 模块。
3. **组件初始化**: 所有组件在模块加载时初始化，使用当前关卡 ID。
4. **API 封装**: 该类封装了 Minecraft 服务端 API 的组件工厂，提供了类型化的访问。
5. **全局访问**: 组件可以通过 `LevelServer.组件名` 全局访问。

## 与网易 API 的关系

`LevelServer` 是对网易 Minecraft 服务端 API 的封装，底层使用 `mod.server.extraServerApi` 模块。每个属性对应一个服务端组件，可以通过这些组件访问 Minecraft 服务端的各种功能。

例如：
- `LevelServer.command` 对应 `compServer.CreateCommand(levelId)`
- `LevelServer.message` 对应 `compServer.CreateMsg(levelId)`

## 常见用途

1. **命令执行**: 通过 `command` 组件执行服务器命令。
2. **消息发送**: 通过 `message` 组件向玩家发送消息。
3. **世界修改**: 通过 `block`、`blockEntity`、`biome` 组件修改世界。
4. **游戏控制**: 通过 `game`、`time`、`weather` 组件控制游戏状态。
5. **实体管理**: 通过 `mobSpawn`、`projectile` 组件管理实体。
6. **配方管理**: 通过 `recipe` 组件管理合成配方。
7. **红石控制**: 通过 `redstone` 组件控制红石信号。

## 与客户端关卡的差异

| 特性 | 服务端 (`architect.level.server`) | 客户端 (`architect.level.client`) |
|------|-----------------------------------|-----------------------------------|
| 类类型 | 静态类（类属性） | 单例类（实例属性） |
| 组件类型 | 服务端组件 | 客户端组件 |
| 功能重点 | 世界管理、命令执行、实体生成 | 玩家控制、UI显示、视觉效果 |
| 访问方式 | `LevelServer.组件名` | `LevelClient.getInstance().组件名` |
| 适用环境 | 服务端脚本 | 客户端脚本 |
