# 数学工具 (Math Utils) API

`architect.math.utils` 模块提供了客户端数学工具函数，包括坐标转换、碰撞检测和实体查询等功能。

## 全局变量

### `level`

- **类型**: `LevelClient`
- **说明**: `LevelClient` 的单例实例。

### `screenWidth`, `screenHeight`

- **类型**: 整数
- **说明**: 屏幕宽度和高度（像素）。

## 相机和投影函数

### `localViewMatrix()`

获取本地相机的视图矩阵。

- **返回值**: (`Matrix`) 视图矩阵。

**实现细节**:
1. 获取相机位置和朝向。
2. 计算观察目标位置（相机位置 + 朝向）。
3. 使用 `lookAt` 函数创建视图矩阵。

### `localProjectionMatrix()`

获取本地相机的投影矩阵。

- **返回值**: (`Matrix`) 透视投影矩阵。

**参数**:
- 视野 (FOV): 从相机组件获取。
- 宽高比: `screenWidth / screenHeight`
- 近裁剪面: 0.1
- 远裁剪面: 100

## 坐标转换函数

### `worldPosToScreenPos(worldPoint)`

将世界坐标转换为屏幕坐标。

- **`worldPoint`**: (元组) 世界坐标 `(x, y, z)`。
- **返回值**: (`Vector3`) 屏幕坐标 `(x, y, depth)`。

**实现细节**:
1. 使用单位矩阵作为模型矩阵。
2. 使用本地视图矩阵和投影矩阵。
3. 调用 `worldToScreen` 函数进行转换。

### `screenPosToWorldPos(screenPoint, depth)`

将屏幕坐标转换为世界坐标。

- **`screenPoint`**: (元组) 屏幕坐标 `(x, y)`。
- **`depth`**: (浮点数) 深度值（从相机到点的距离）。
- **返回值**: (`Vector3`) 世界坐标。

**实现细节**:
1. 将屏幕坐标转换为 `Vector3`，z 坐标为 0。
2. 使用单位矩阵作为模型矩阵。
3. 使用本地视图矩阵和投影矩阵。
4. 调用 `screenToWorld` 函数进行转换。

## 碰撞检测函数

### `pointInBox(point, box)`

检查点是否在轴对齐的盒子内（以原点为中心）。

- **`point`**: (元组) 点坐标 `(x, y, z)`。
- **`box`**: (元组) 盒子尺寸 `(width, height, depth)`。
- **返回值**: (布尔值) 点是否在盒子内。

**假设**: 盒子以原点为中心，范围从 `-size/2` 到 `size/2`。

### `pointInAabb(point, min, max)`

检查点是否在轴对齐边界框 (AABB) 内。

- **`point`**: (元组) 点坐标 `(x, y, z)`。
- **`min`**: (元组) AABB 最小点 `(min_x, min_y, min_z)`。
- **`max`**: (元组) AABB 最大点 `(max_x, max_y, max_z)`。
- **返回值**: (布尔值) 点是否在 AABB 内。

## 实体查询函数

### `boxOverlap3dClient(pos, rot, size, debug=False)`

在客户端查询与指定盒子重叠的实体。

- **`pos`**: (元组) 盒子位置 `(x, y, z)`。
- **`rot`**: (元组) 盒子旋转 `(rx, ry, rz)`（弧度）。
- **`size`**: (元组) 盒子尺寸 `(width, height, depth)`。
- **`debug`**: (布尔值, 默认值 `False`) 是否启用调试模式。
- **返回值**: (列表) 与盒子重叠的实体 ID 列表。

**算法**:
1. 计算盒子的投影半径（在 XZ 平面上的最大半径）。
2. 使用 `GetEntitiesInSquareArea` 获取大致区域内的实体。
3. 创建盒子的世界变换矩阵的逆矩阵。
4. 将每个实体的中心点转换到盒子局部坐标系。
5. 使用 `pointInBox` 检查是否在盒子内。

### `boxOverlap3dForward(entityId, size)`

查询实体前方指定尺寸的盒子内的其他实体。

- **`entityId`**: (字符串) 实体 ID。
- **`size`**: (元组) 盒子尺寸 `(width, height, depth)`。
- **返回值**: (列表) 前方盒子内的实体 ID 列表（不包括自身）。

**实现细节**:
1. 获取实体的位置和旋转。
2. 获取实体的朝向向量。
3. 在位置前方 2 个单位处创建盒子。
4. 调用 `boxOverlap3dClient` 进行查询。
5. 从结果中移除自身实体。

### `forward(entityId)`

获取实体在水平面上的朝向向量（忽略垂直分量）。

- **`entityId`**: (字符串) 实体 ID。
- **返回值**: (`Vector3`) 归一化的水平朝向向量。

### `facing(entityId)`

获取实体的完整朝向向量。

- **`entityId`**: (字符串) 实体 ID。
- **返回值**: (`Vector3`) 朝向向量。

### `entityAabbDef(entityId)`

获取实体的轴对齐边界框 (AABB) 定义。

- **`entityId`**: (字符串) 实体 ID。
- **返回值**: (元组) `((min_x, min_y, min_z), (max_x, max_y, max_z))`。

**实现细节**:
1. 使用 Molang 表达式查询实体的头部骨骼 AABB。
2. 将结果从像素单位转换为方块单位（除以 16）。

## 默认过滤器

### `defaultFilters`

- **类型**: 字典
- **说明**: 默认的实体过滤器配置。

**配置内容**:
```json
{
    "any_of": [
        {
            "subject": "other",
            "test": "is_family",
            "value": "player"
        },
        {
            "subject": "other",
            "test": "is_family",
            "value": "mob"
        }
    ]
}
```

**含义**: 匹配玩家 (`player`) 或生物 (`mob`) 家族的实体。

## 使用示例

### 1. 坐标转换

```python
from ..architect.math.utils import worldPosToScreenPos, screenPosToWorldPos

# 世界坐标转屏幕坐标
world_point = (100, 64, 200)
screen_point = worldPosToScreenPos(world_point)
print(f'屏幕坐标: ({screen_point.x}, {screen_point.y})')

# 屏幕坐标转世界坐标（深度为10）
screen_coords = (960, 540)  # 屏幕中心
world_point = screenPosToWorldPos(screen_coords, 10)
print(f'世界坐标: ({world_point.x}, {world_point.y}, {world_point.z})')
```

### 2. 碰撞检测

```python
from ..architect.math.utils import pointInBox, pointInAabb

# 检查点是否在盒子内
point = (1, 2, 3)
box_size = (10, 10, 10)  # 10x10x10的盒子
in_box = pointInBox(point, box_size)  # True

# 检查点是否在AABB内
min_point = (0, 0, 0)
max_point = (5, 5, 5)
in_aabb = pointInAabb(point, min_point, max_point)  # False
```

### 3. 实体查询

```python
from ..architect.math.utils import boxOverlap3dClient, boxOverlap3dForward

# 查询指定盒子内的实体
position = (0, 64, 0)
rotation = (0, 0, 0)  # 无旋转
size = (5, 3, 5)  # 5x3x5的盒子
entities = boxOverlap3dClient(position, rotation, size)
print(f'盒子内的实体: {entities}')

# 查询玩家前方的实体
player_id = 'player_123'
forward_entities = boxOverlap3dForward(player_id, (3, 2, 3))
print(f'玩家前方的实体: {forward_entities}')
```

### 4. 实体朝向

```python
from ..architect.math.utils import forward, facing

entity_id = 'player_123'

# 获取水平朝向
horizontal_dir = forward(entity_id)
print(f'水平朝向: {horizontal_dir}')

# 获取完整朝向
full_dir = facing(entity_id)
print(f'完整朝向: {full_dir}')
```

### 5. 实体AABB

```python
from ..architect.math.utils import entityAabbDef

entity_id = 'zombie_456'
(min_point, max_point) = entityAabbDef(entity_id)
print(f'AABB最小点: {min_point}')
print(f'AABB最大点: {max_point}')
```

## 注意事项

1. **客户端专用**: 该模块仅用于客户端环境，依赖客户端 API。
2. **性能考虑**: `boxOverlap3dClient` 和 `entityAabbDef` 函数可能较慢，避免每帧调用。
3. **坐标系统**: 所有坐标使用 Minecraft 的世界坐标系统（1 方块 = 1 单位）。
4. **单位转换**: `entityAabbDef` 返回的坐标已从像素单位转换为方块单位。
5. **屏幕坐标**: 屏幕坐标原点在左上角，x 向右增加，y 向下增加。
6. **碰撞精度**: `boxOverlap3dClient` 使用近似算法，可能不适用于精确碰撞检测。
