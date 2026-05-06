# 客户端关卡 (Level Client) API

`architect.level.client` 模块提供了客户端关卡功能，封装了 Minecraft 客户端 API 的关卡相关组件。

## `LevelClient` 类

`LevelClient` 类是客户端关卡的单例类，提供了对客户端关卡组件的便捷访问。

### 构造函数

#### `__init__(self)`

初始化客户端关卡实例。

### 属性

#### `levelId`

- **类型**: 字符串
- **说明**: 当前关卡的 ID。

#### `localPlayerId`

- **类型**: 字符串
- **说明**: 本地玩家的 ID。

#### `localPlayer`

- **类型**: `PlayerClient`
- **说明**: 本地玩家组件。

#### `achievement`

- **类型**: `AchievementClient`
- **说明**: 成就组件。

#### `actorRender`

- **类型**: `ActorRenderClient`
- **说明**: 角色渲染组件。

#### `biome`

- **类型**: `BiomeClient`
- **说明**: 生物群系组件。

#### `block`

- **类型**: `BlockClient`
- **说明**: 方块组件。

#### `blockGeometry`

- **类型**: `BlockGeometryClient`
- **说明**: 方块几何组件。

#### `blockInfo`

- **类型**: `BlockInfoClient`
- **说明**: 方块信息组件。

#### `blockUseEventWhiteList`

- **类型**: `BlockUseEventWhiteListClient`
- **说明**: 方块使用事件白名单组件。

#### `camera`

- **类型**: `CameraClient`
- **说明**: 相机组件。

#### `chunkSource`

- **类型**: `ChunkSourceClient`
- **说明**: 区块源组件。

#### `configClient`

- **类型**: `ConfigClient`
- **说明**: 客户端配置组件。

#### `customAudio`

- **类型**: `CustomAudioClient`
- **说明**: 自定义音频组件。

#### `dimension`

- **类型**: `DimensionClient`
- **说明**: 维度组件。

#### `drawing`

- **类型**: `DrawingClient`
- **说明**: 绘图组件。

#### `fog`

- **类型**: `FogClient`
- **说明**: 雾组件。

#### `game`

- **类型**: `GameClient`
- **说明**: 游戏组件。

#### `model`

- **类型**: `ModelClient`
- **说明**: 模型组件。

#### `neteaseShop`

- **类型**: `NeteaseShopClient`
- **说明**: 网易商店组件。

#### `operation`

- **类型**: `OperationClient`
- **说明**: 操作组件。

#### `playerView`

- **类型**: `PlayerViewClient`
- **说明**: 玩家视图组件。

#### `postProcess`

- **类型**: `PostProcessClient`
- **说明**: 后处理组件。

#### `recipe`

- **类型**: `RecipeClient`
- **说明**: 配方组件。

#### `skyRender`

- **类型**: `SkyRenderClient`
- **说明**: 天空渲染组件。

#### `textBoard`

- **类型**: `TextBoardClient`
- **说明**: 文本板组件。

#### `textNotify`

- **类型**: `TextNotifyClient`
- **说明**: 文本通知组件。

#### `virtualWorld`

- **类型**: `VirtualWorldClient`
- **说明**: 虚拟世界组件。

#### `item`

- **类型**: `ItemClient`
- **说明**: 物品组件。

#### `neteaseWindow`

- **类型**: `NeteaseWindowClient`
- **说明**: 网易窗口组件。

### 静态方法

#### `getInstance()`

获取 `LevelClient` 的单例实例。

- **返回值**: (`LevelClient`) 单例实例。

## 使用示例

### 1. 获取单例实例

```python
from ..architect.level.client import LevelClient

# 获取 LevelClient 单例
level_client = LevelClient.getInstance()

# 访问关卡 ID
level_id = level_client.levelId
print(f'关卡 ID: {level_id}')

# 访问本地玩家 ID
player_id = level_client.localPlayerId
print(f'本地玩家 ID: {player_id}')
```

### 2. 使用客户端组件

```python
from ..architect.level.client import LevelClient

level_client = LevelClient.getInstance()

# 使用相机组件
camera = level_client.camera
camera.SetFov(70.0)  # 设置视野

# 使用文本通知组件
text_notify = level_client.textNotify
text_notify.NotifyOneMessage(player_id, 'Hello, World!', '§a')

# 使用物品组件
item = level_client.item
item_list = item.GetPlayerAllItems(player_id)

# 使用后处理组件
post_process = level_client.postProcess
post_process.SetPostProcessEffect('bloom', True)
```

### 3. 直接访问组件方法

```python
from ..architect.level.client import LevelClient

level_client = LevelClient.getInstance()

# 获取玩家位置
player_pos = level_client.localPlayer.GetPos()
print(f'玩家位置: {player_pos}')

# 设置相机模式
level_client.camera.SetCameraMode('first_person')

# 显示文本板
level_client.textBoard.SetText('player_123', 'Welcome to the game!')
```

## 注意事项

1. **单例模式**: `LevelClient` 是单例类，使用 `getInstance()` 方法获取实例。
2. **客户端专用**: 该模块仅用于客户端环境，服务端应使用 `architect.level.server` 模块。
3. **组件初始化**: 所有组件在 `__init__` 中初始化，使用当前关卡 ID。
4. **API 封装**: 该类封装了 Minecraft 客户端 API 的组件工厂，提供了类型化的访问。
5. **线程安全**: 单例实例在首次调用 `getInstance()` 时创建，后续调用返回同一实例。

## 与网易 API 的关系

`LevelClient` 是对网易 Minecraft 客户端 API 的封装，底层使用 `mod.client.extraClientApi` 模块。每个属性对应一个客户端组件，可以通过这些组件访问 Minecraft 的各种功能。

例如：
- `level_client.camera` 对应 `compClient.CreateCamera(levelId)`
- `level_client.textNotify` 对应 `compClient.CreateTextNotifyClient(levelId)`

## 常见用途

1. **玩家控制**: 通过 `localPlayer` 组件控制玩家行为。
2. **UI 显示**: 通过 `textNotify`、`textBoard` 组件显示文本信息。
3. **视觉效果**: 通过 `camera`、`postProcess`、`fog` 组件调整视觉效果。
4. **世界交互**: 通过 `block`、`item`、`biome` 组件与世界交互。
5. **游戏设置**: 通过 `configClient`、`game` 组件调整游戏设置。
