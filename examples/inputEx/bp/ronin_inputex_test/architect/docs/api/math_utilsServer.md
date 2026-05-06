# 服务端数学工具 (Math Utils Server) API

`architect.math.utilsServer` 模块提供了服务端数学工具函数，包括碰撞检测和实体查询等功能。

## 函数

### `pointInBox(point, box)`

检查点是否在轴对齐的盒子内（以原点为中心）。

- **`point`**: (元组) 点坐标 `(x, y, z)`。
- **`box`**: (元组) 盒子尺寸 `(width, height, depth)`。
- **返回值**: (布尔值) 点是否在盒子内。

**假设**: 盒子以原点为中心，范围从 `-size/2` 到 `size/2`。

**实现**:
```python
size = box
half_x = size[0] / 2
half_y = size[1] / 2
half_z = size[2] / 2
return -half_x <= point[0] <= half_x and -half_y <= point[1] <= half_y and -half_z <= point[2] <= half_z
```

### `boxOverlap3dServer(pos, rot, size, dim, filter=None)`

在服务端查询与指定盒子重叠的实体。

- **`pos`**: (元组) 盒子位置 `(x, y, z)`。
- **`rot`**: (元组) 盒子旋转 `(rx, ry, rz)`（弧度）。
- **`size`**: (元组) 盒子尺寸 `(width, height, depth)`。
- **`dim`**: (整数) 维度 ID。
- **`filter`**: (函数, 可选) 实体过滤器函数，接受实体 ID 返回布尔值。
- **返回值**: (列表) 与盒子重叠的实体 ID 列表。

**算法**:
1. 计算盒子的投影半径（在 XZ 平面上的最大半径）。
2. 使用 `LevelServer.game.GetEntitiesInSquareArea` 获取大致区域内的实体。
3. 创建盒子的世界变换矩阵的逆矩阵。
4. 将每个实体的中心点转换到盒子局部坐标系。
5. 使用 `pointInBox` 检查是否在盒子内。
6. 如果提供了过滤器函数，应用过滤器。

### `boxOverlap3dForward(entityId, size)`

查询实体前方指定尺寸的盒子内的其他实体。

- **`entityId`**: (字符串) 实体 ID。
- **`size`**: (元组) 盒子尺寸 `(width, height, depth)`。
- **返回值**: (列表) 前方盒子内的实体 ID 列表（不包括自身）。

**实现细节**:
1. 获取实体的位置、旋转和维度。
2. 获取实体的朝向向量。
3. 在位置前方 `length/2` 个单位处创建盒子（`length = size[2]`）。
4. 调用 `boxOverlap3dServer` 进行查询。
5. 应用默认过滤器，排除物品实体和经验球。
6. 从结果中移除自身实体。

### `facing(entityId)`

获取实体的完整朝向向量。

- **`entityId`**: (字符串) 实体 ID。
- **返回值**: (`Vector3`) 朝向向量。

### `forward(entityId, dist=1)`

获取实体在水平面上的朝向向量，并乘以指定距离。

- **`entityId`**: (字符串) 实体 ID。
- **`dist`**: (浮点数, 默认值 `1`) 距离乘数。
- **返回值**: (`Vector3`) 归一化的水平朝向向量乘以距离。

## 使用示例

### 1. 碰撞检测

```python
from ..architect.math.utilsServer import pointInBox

# 检查点是否在盒子内
point = (1, 2, 3)
box_size = (10, 10, 10)  # 10x10x10的盒子
in_box = pointInBox(point, box_size)  # True
```

### 2. 实体查询

```python
from ..architect.math.utilsServer import boxOverlap3dServer, boxOverlap3dForward

# 查询指定盒子内的实体
position = (0, 64, 0)
rotation = (0, 0, 0)  # 无旋转
size = (5, 3, 5)  # 5x3x5的盒子
dimension = 0  # 主世界
entities = boxOverlap3dServer(position, rotation, size, dimension)
print(f'盒子内的实体: {entities}')

# 使用自定义过滤器
def player_filter(entity_id):
    from ..basic import compServer
    from mod.common.minecraftEnum import EntityType
    entity_type = compServer.CreateEngineType(entity_id).GetEngineType()
    return entity_type == EntityType.Player

player_entities = boxOverlap3dServer(position, rotation, size, dimension, player_filter)
print(f'盒子内的玩家: {player_entities}')
```

### 3. 前方实体查询

```python
from ..architect.math.utilsServer import boxOverlap3dForward

# 查询玩家前方的实体
player_id = 'player_123'
size = (3, 2, 5)  # 宽度3，高度2，深度5的盒子
forward_entities = boxOverlap3dForward(player_id, size)
print(f'玩家前方的实体: {forward_entities}')
```

### 4. 实体朝向

```python
from ..architect.math.utilsServer import facing, forward

entity_id = 'zombie_456'

# 获取完整朝向
full_dir = facing(entity_id)
print(f'完整朝向: {full_dir}')

# 获取水平朝向（距离为2）
horizontal_dir = forward(entity_id, 2)
print(f'水平朝向（距离2）: {horizontal_dir}')
```

## 与客户端版本的差异

| 特性 | 服务端 (`architect.math.utilsServer`) | 客户端 (`architect.math.utils`) |
|------|---------------------------------------|---------------------------------|
| 环境 | 服务端 | 客户端 |
| 依赖 | `LevelServer`, `compServer` | `LevelClient`, `compClient` |
| 维度支持 | 支持维度参数 | 无维度参数 |
| 过滤器 | 支持自定义过滤器函数 | 无过滤器支持 |
| 排除实体 | 自动排除物品实体和经验球 | 不自动排除 |
| 前方查询 | 盒子中心在实体前方 `length/2` 处 | 盒子中心在实体前方 2 个单位处 |
| 坐标转换 | 无屏幕坐标转换 | 支持世界-屏幕坐标转换 |

## 注意事项

1. **服务端专用**: 该模块仅用于服务端环境，依赖服务端 API。
2. **性能考虑**: `boxOverlap3dServer` 函数可能较慢，避免每帧调用。
3. **维度参数**: 必须提供正确的维度 ID，否则可能查询不到实体。
4. **过滤器函数**: 过滤器函数应快速返回，避免影响性能。
5. **坐标系统**: 所有坐标使用 Minecraft 的世界坐标系统（1 方块 = 1 单位）。
6. **碰撞精度**: 使用近似算法，可能不适用于精确碰撞检测。
7. **实体类型**: `boxOverlap3dForward` 自动排除物品实体 (`EntityType.ItemEntity`) 和经验球 (`EntityType.Experience`)。

## 高级用法

### 自定义过滤器

```python
from ..architect.math.utilsServer import boxOverlap3dServer
from ..basic import compServer
from mod.common.minecraftEnum import EntityType

def custom_filter(entity_id):
    """自定义过滤器：只返回生命值大于10的怪物"""
    engine_type = compServer.CreateEngineType(entity_id).GetEngineType()
    
    # 只检查怪物
    if engine_type not in (EntityType.Monster, EntityType.Animal):
        return False
    
    # 检查生命值
    attr_comp = compServer.CreateAttr(entity_id)
    health = attr_comp.GetAttrValue(AttrType.HEALTH)
    return health > 10

# 使用自定义过滤器
entities = boxOverlap3dServer(
    position=(0, 64, 0),
    rotation=(0, 0, 0),
    size=(10, 10, 10),
    dim=0,
    filter=custom_filter
)
```

### 组合查询

```python
from ..architect.math.utilsServer import boxOverlap3dForward, forward

def get_entities_in_cone(entity_id, radius, angle_degrees):
    """查询实体前方锥形区域内的实体"""
    # 获取实体位置和朝向
    pos = compServer.CreatePos(entity_id).GetPos()
    dir_vec = forward(entity_id)  # 归一化朝向向量
    
    # 创建多个盒子模拟锥形
    results = []
    for i in range(1, 6):
        # 沿朝向方向创建盒子
        box_pos = (
            pos[0] + dir_vec.x * i * 2,
            pos[1] + dir_vec.y * i * 2,
            pos[2] + dir_vec.z * i * 2
        )
        box_size = (radius * i / 3, 3, radius * i / 3)
        
        # 查询盒子内的实体
        box_entities = boxOverlap3dServer(
            box_pos,
            (0, 0, 0),  # 无旋转
            box_size,
            compServer.CreateDimension(entity_id).GetEntityDimensionId()
        )
        
        # 过滤掉自身
        if entity_id in box_entities:
            box_entities.remove(entity_id)
        
        results.extend(box_entities)
    
    # 去重
    return list(set(results))
```
