# 4x4 矩阵运算 (Mat4) API

`architect.math.mat4` 模块提供了 4x4 矩阵的创建、变换和运算功能，用于 3D 图形计算。

## 依赖

- `mod.common.utils.mcmath.Matrix` - Minecraft 的矩阵类
- `mod.common.utils.mcmath.Vector3` - Minecraft 的向量类
- `architect.math.vec3` - 向量运算函数

## 基本矩阵函数

### `identity()`

创建单位矩阵。

- **返回值**: (`Matrix`) 4x4 单位矩阵。

**示例**:
```python
from ..architect.math.mat4 import identity

mat = identity()
# 矩阵内容:
# [1, 0, 0, 0]
# [0, 1, 0, 0]
# [0, 0, 1, 0]
# [0, 0, 0, 1]
```

### `multiply(a, b)`

矩阵乘法。

- **`a`**: (`Matrix`) 第一个矩阵。
- **`b`**: (`Matrix`) 第二个矩阵。
- **返回值**: (`Matrix`) 矩阵乘积 `a * b`。

**注意**: 矩阵乘法不满足交换律，顺序很重要。

### `transpose(m)`

矩阵转置。

- **`m`**: (`Matrix`) 输入矩阵。
- **返回值**: (`Matrix`) 转置矩阵。

### `inverse(m)`

矩阵求逆。

- **`m`**: (`Matrix`) 输入矩阵。
- **返回值**: (`Matrix`) 逆矩阵。

## 变换矩阵

### `translate(v)`

创建平移矩阵。

- **`v`**: (`Vector3`) 平移向量。
- **返回值**: (`Matrix`) 平移矩阵。

**矩阵形式**:
```
[1, 0, 0, v.x]
[0, 1, 0, v.y]
[0, 0, 1, v.z]
[0, 0, 0, 1]
```

### `rotateAxis(axis, angle)`

创建绕任意轴旋转的矩阵。

- **`axis`**: (`Vector3`) 旋转轴（会被归一化）。
- **`angle`**: (浮点数) 旋转角度（弧度）。
- **返回值**: (`Matrix`) 旋转矩阵。

### `rotateX(angle)`

创建绕 X 轴旋转的矩阵。

- **`angle`**: (浮点数) 旋转角度（弧度）。
- **返回值**: (`Matrix`) 旋转矩阵。

**矩阵形式**:
```
[1, 0, 0, 0]
[0, cos(angle), -sin(angle), 0]
[0, sin(angle), cos(angle), 0]
[0, 0, 0, 1]
```

### `rotateY(angle)`

创建绕 Y 轴旋转的矩阵。

- **`angle`**: (浮点数) 旋转角度（弧度）。
- **返回值**: (`Matrix`) 旋转矩阵。

**矩阵形式**:
```
[cos(angle), 0, sin(angle), 0]
[0, 1, 0, 0]
[-sin(angle), 0, cos(angle), 0]
[0, 0, 0, 1]
```

### `rotateZ(angle)`

创建绕 Z 轴旋转的矩阵。

- **`angle`**: (浮点数) 旋转角度（弧度）。
- **返回值**: (`Matrix`) 旋转矩阵。

**矩阵形式**:
```
[cos(angle), -sin(angle), 0, 0]
[sin(angle), cos(angle), 0, 0]
[0, 0, 1, 0]
[0, 0, 0, 1]
```

### `rotateXYZ(roll, yaw, pitch)`

创建绕 Z、Y、X 轴依次旋转的矩阵（欧拉角）。

- **`roll`**: (浮点数) 绕 Z 轴旋转角度（弧度）。
- **`yaw`**: (浮点数) 绕 Y 轴旋转角度（弧度）。
- **`pitch`**: (浮点数) 绕 X 轴旋转角度（弧度）。
- **返回值**: (`Matrix`) 旋转矩阵。

**注意**: 旋转顺序为 Z → Y → X（矩阵乘法从右到左应用）。

### `scale(s)`

创建缩放矩阵。

- **`s`**: (`Vector3`) 缩放向量。
- **返回值**: (`Matrix`) 缩放矩阵。

**矩阵形式**:
```
[s.x, 0, 0, 0]
[0, s.y, 0, 0]
[0, 0, s.z, 0]
[0, 0, 0, 1]
```

### `transform(m, t, r, s)`

创建标准模型变换矩阵。

- **`m`**: (`Matrix`) 父节点变换矩阵（通常为单位矩阵）。
- **`t`**: (`Vector3`) 平移向量。
- **`r`**: (`Vector3`) 旋转欧拉角（弧度）。
- **`s`**: (`Vector3`) 缩放向量。
- **返回值**: (`Matrix`) 变换矩阵。

**变换顺序**: 先缩放 (S)，再旋转 (R)，最后平移 (T)。  
**矩阵公式**: `M_final = m * T * R * S`

## 视图和投影矩阵

### `lookAt(eye, target, up)`

创建视图矩阵（LookAt 矩阵）。

- **`eye`**: (`Vector3`) 相机位置。
- **`target`**: (`Vector3`) 观察目标位置。
- **`up`**: (`Vector3`) 上方向向量。
- **返回值**: (`Matrix`) 视图矩阵。

**注意**: 使用右手坐标系，相机看向 -Z 方向。

### `perspective(fov_degrees, aspect, near, far)`

创建透视投影矩阵。

- **`fov_degrees`**: (浮点数) 垂直视场角（角度制）。
- **`aspect`**: (浮点数) 宽高比（宽度/高度）。
- **`near`**: (浮点数) 近裁剪平面距离。
- **`far`**: (浮点数) 远裁剪平面距离。
- **返回值**: (`Matrix`) 透视投影矩阵。

**注意**: 使用右手坐标系，NDC 的 z 范围映射到 [-1, 1]。

## 坐标变换

### `transformPoint(m, point)`

使用矩阵变换一个点（包含平移影响）。

- **`m`**: (`Matrix`) 变换矩阵。
- **`point`**: (`Vector3`) 要变换的点。
- **返回值**: (`Vector3`) 变换后的点。

**数学公式**: 将点表示为齐次坐标 `[x, y, z, 1]` 并进行矩阵乘法。

### `transformVector(m, vector)`

使用矩阵变换一个向量（忽略平移影响）。

- **`m`**: (`Matrix`) 变换矩阵。
- **`vector`**: (`Vector3`) 要变换的向量。
- **返回值**: (`Vector3`) 变换后的向量。

**数学公式**: 将向量表示为齐次坐标 `[x, y, z, 0]` 并进行矩阵乘法。

### `localToWorld(modelMatrix, localPoint)`

将模型局部坐标系中的点转换到世界坐标系。

- **`modelMatrix`**: (`Matrix`) 模型到世界的变换矩阵。
- **`localPoint`**: (`Vector3`) 模型局部坐标系中的点。
- **返回值**: (`Vector3`) 世界坐标系中的点。

### `worldToLocal(modelMatrix, worldPoint)`

将世界坐标系中的点转换到模型局部坐标系。

- **`modelMatrix`**: (`Matrix`) 模型到世界的变换矩阵。
- **`worldPoint`**: (`Vector3`) 世界坐标系中的点。
- **返回值**: (`Vector3`) 模型局部坐标系中的点。

### `worldToScreen(modelMatrix, viewMatrix, projectionMatrix, viewport, worldPoint)`

将世界坐标系中的点转换到屏幕坐标系。

- **`modelMatrix`**: (`Matrix`) 模型到世界的变换矩阵。
- **`viewMatrix`**: (`Matrix`) 世界到视图的变换矩阵（摄像机矩阵）。
- **`projectionMatrix`**: (`Matrix`) 视图到投影的变换矩阵。
- **`viewport`**: (元组) 屏幕视口 `(width, height)`。
- **`worldPoint`**: (`Vector3`) 世界坐标系中的点。
- **返回值**: (`Vector3`) 屏幕坐标系中的点 `(x, y, depth)`。

### `screenToWorld(modelMatrix, viewMatrix, projectionMatrix, viewport, screenPoint, depth)`

将屏幕坐标系中的点转换到世界坐标系。

- **`modelMatrix`**: (`Matrix`) 模型到世界的变换矩阵。
- **`viewMatrix`**: (`Matrix`) 世界到视图的变换矩阵（摄像机矩阵）。
- **`projectionMatrix`**: (`Matrix`) 视图到投影的变换矩阵。
- **`viewport`**: (元组) 屏幕视口 `(width, height)`。
- **`screenPoint`**: (`Vector3`) 屏幕坐标系中的点 `(x, y, depth)`。
- **`depth`**: (浮点数) 深度值（从摄像机到点的距离）。
- **返回值**: (`Vector3`) 世界坐标系中的点。

## 使用示例

### 1. 创建变换矩阵

```python
from ..architect.math.mat4 import identity, translate, rotateY, scale, transform
from mod.common.utils.mcmath import Vector3

# 创建单位矩阵
mat = identity()

# 创建平移矩阵
translation = translate(Vector3(10, 5, 0))

# 创建旋转矩阵（绕Y轴旋转45度）
import math
rotation = rotateY(math.radians(45))

# 创建缩放矩阵
scaling = scale(Vector3(2, 2, 2))

# 组合变换：先缩放，再旋转，最后平移
model_matrix = translation * rotation * scaling
```

### 2. 3D 相机系统

```python
from ..architect.math.mat4 import lookAt, perspective
from mod.common.utils.mcmath import Vector3

# 创建相机
camera_pos = Vector3(0, 10, 20)
camera_target = Vector3(0, 0, 0)
camera_up = Vector3(0, 1, 0)

# 视图矩阵
view_matrix = lookAt(camera_pos, camera_target, camera_up)

# 投影矩阵
fov = 60  # 度
aspect_ratio = 16 / 9  # 宽高比
near_plane = 0.1
far_plane = 1000
projection_matrix = perspective(fov, aspect_ratio, near_plane, far_plane)
```

### 3. 坐标变换

```python
from ..architect.math.mat4 import localToWorld, worldToScreen
from mod.common.utils.mcmath import Vector3

# 假设已有模型矩阵、视图矩阵、投影矩阵
model_matrix = ...  # 模型变换矩阵
view_matrix = ...   # 视图矩阵
projection_matrix = ...  # 投影矩阵
viewport = (1920, 1080)  # 屏幕分辨率

# 局部坐标点
local_point = Vector3(0, 0, 0)  # 模型原点

# 转换到世界坐标
world_point = localToWorld(model_matrix, local_point)

# 转换到屏幕坐标
screen_point = worldToScreen(
    model_matrix, view_matrix, projection_matrix, 
    viewport, world_point
)

print(f'屏幕坐标: ({screen_point.x}, {screen_point.y})')
```

### 4. 动画变换

```python
from ..architect.math.mat4 import identity, translate, rotateY, transform
from mod.common.utils.mcmath import Vector3
import math
import time

class AnimatedObject:
    def __init__(self):
        self.position = Vector3(0, 0, 0)
        self.rotation = Vector3(0, 0, 0)  # 欧拉角
        self.scale = Vector3(1, 1, 1)
        self.parent_matrix = identity()
    
    def update(self, delta_time):
        # 更新旋转（绕Y轴旋转）
        self.rotation.y += math.radians(90) * delta_time
        
        # 创建变换矩阵
        transform_matrix = transform(
            self.parent_matrix,
            self.position,
            self.rotation,
            self.scale
        )
        
        return transform_matrix
```

## 注意事项

1. **右手坐标系**: 所有函数使用右手坐标系，Z 轴指向屏幕外。
2. **矩阵顺序**: 矩阵乘法从右到左应用变换。
3. **角度单位**: 旋转函数使用弧度制，`perspective` 函数使用角度制。
4. **性能**: 矩阵运算较复杂，避免每帧创建大量矩阵。
5. **逆矩阵**: 不是所有矩阵都有逆矩阵（奇异矩阵无法求逆）。
6. **齐次坐标**: 点和向量的变换使用不同的齐次坐标表示。
7. **欧拉角**: 使用 ZYX 顺序（roll, yaw, pitch），注意万向节锁问题。
