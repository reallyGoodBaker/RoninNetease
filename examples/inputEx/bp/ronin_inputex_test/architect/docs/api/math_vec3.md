# 三维向量运算 (Vec3) API

`architect.math.vec3` 模块提供了三维向量的创建、运算和变换功能。

## 依赖

- `mod.common.utils.mcmath.Vector3` - Minecraft 的向量类

## 向量创建

### `vec(tup=(0,0,0))`

创建 `Vector3` 对象。

- **`tup`**: (元组, 可选) 包含三个浮点数的元组 `(x, y, z)`，默认为 `(0, 0, 0)`。
- **返回值**: (`Vector3`) 三维向量。

**示例**:
```python
from ..architect.math.vec3 import vec

# 创建零向量
v0 = vec()  # (0, 0, 0)

# 从元组创建
v1 = vec((1, 2, 3))  # (1, 2, 3)
v2 = vec((0, 1, 0))  # (0, 1, 0)
```

## 基本运算

### `add(a, b)`

向量加法。

- **`a`**: (`Vector3`) 第一个向量。
- **`b`**: (`Vector3`) 第二个向量。
- **返回值**: (`Vector3`) 向量和 `a + b`。

### `sub(a, b)`

向量减法。

- **`a`**: (`Vector3`) 第一个向量。
- **`b`**: (`Vector3`) 第二个向量。
- **返回值**: (`Vector3`) 向量差 `a - b`。

### `mul(a, b)`

向量与标量乘法。

- **`a`**: (`Vector3`) 向量。
- **`b`**: (浮点数或整数) 标量。
- **返回值**: (`Vector3`) 缩放后的向量 `a * b`。

### `div(a, b)`

向量与标量除法。

- **`a`**: (`Vector3`) 向量。
- **`b`**: (浮点数或整数) 标量。
- **返回值**: (`Vector3`) 缩放后的向量 `a / b`。

## 向量运算

### `dot(a, b)`

向量点积（内积）。

- **`a`**: (`Vector3`) 第一个向量。
- **`b`**: (`Vector3`) 第二个向量。
- **返回值**: (浮点数) 点积结果 `a · b`。

**数学公式**: `a.x * b.x + a.y * b.y + a.z * b.z`

### `cross(a, b)`

向量叉积（外积）。

- **`a`**: (`Vector3`) 第一个向量。
- **`b`**: (`Vector3`) 第二个向量。
- **返回值**: (`Vector3`) 叉积结果 `a × b`。

**数学公式**: 
```
x = a.y * b.z - a.z * b.y
y = a.z * b.x - a.x * b.z
z = a.x * b.y - a.y * b.x
```

### `modulo(a)`

向量模长（长度）。

- **`a`**: (`Vector3`) 向量。
- **返回值**: (浮点数) 向量长度 `|a|`。

**数学公式**: `sqrt(a.x² + a.y² + a.z²)`

### `moduloSqrt(a)`

向量模长的平方。

- **`a`**: (`Vector3`) 向量。
- **返回值**: (浮点数) 向量长度的平方 `|a|²`。

**数学公式**: `a.x² + a.y² + a.z²`

### `normalize(a)`

向量归一化。

- **`a`**: (`Vector3`) 向量。
- **返回值**: (`Vector3`) 单位向量，方向与 `a` 相同。

**注意**: 如果输入向量长度为零，返回零向量。

### `compare(a, b)`

比较两个向量的长度。

- **`a`**: (`Vector3`) 第一个向量。
- **`b`**: (`Vector3`) 第二个向量。
- **返回值**: (浮点数) `|a|² - |b|²`。

**解释**:
- 如果返回值 > 0，则 `|a| > |b|`
- 如果返回值 < 0，则 `|a| < |b|`
- 如果返回值 = 0，则 `|a| = |b|`

## 向量变换

### `clamp(v, min, max)`

限制向量的长度在指定范围内。

- **`v`**: (`Vector3`) 输入向量。
- **`min`**: (浮点数) 最小长度。
- **`max`**: (浮点数) 最大长度。
- **返回值**: (`Vector3`) 限制后的向量。

**算法**:
1. 计算向量长度的平方 `lenSqrt = |v|²`
2. 如果 `lenSqrt > max²`，将向量缩放为长度 `max`
3. 如果 `lenSqrt < min²`，将向量缩放为长度 `min`
4. 否则返回原向量

### `lerp(a, b, t)`

线性插值。

- **`a`**: (`Vector3`) 起始向量。
- **`b`**: (`Vector3`) 结束向量。
- **`t`**: (浮点数) 插值因子，范围 [0, 1]。
- **返回值**: (`Vector3`) 插值结果。

**数学公式**: `a * (1 - t) + b * t`

### `nlerp(a, b, t)`

归一化线性插值（球面线性插值的近似）。

- **`a`**: (`Vector3`) 起始向量（应为单位向量）。
- **`b`**: (`Vector3`) 结束向量（应为单位向量）。
- **`t`**: (浮点数) 插值因子，范围 [0, 1]。
- **返回值**: (`Vector3`) 归一化插值结果。

**算法**: 先进行线性插值，然后归一化结果。

**注意**: 输入向量应为单位向量，否则插值不经过起点和终点。

### `tup(a)`

将 `Vector3` 转换为元组。

- **`a`**: (`Vector3`) 向量。
- **返回值**: (元组) `(x, y, z)`。

## 使用示例

### 1. 基本向量运算

```python
from ..architect.math.vec3 import vec, add, sub, mul, dot, cross

# 创建向量
v1 = vec((1, 2, 3))
v2 = vec((4, 5, 6))

# 向量加法
v_sum = add(v1, v2)  # (5, 7, 9)

# 向量减法
v_diff = sub(v1, v2)  # (-3, -3, -3)

# 标量乘法
v_scaled = mul(v1, 2)  # (2, 4, 6)

# 点积
dot_product = dot(v1, v2)  # 1*4 + 2*5 + 3*6 = 32

# 叉积
cross_product = cross(v1, v2)  # (-3, 6, -3)
```

### 2. 向量长度和方向

```python
from ..architect.math.vec3 import vec, modulo, moduloSqrt, normalize, clamp

v = vec((3, 4, 0))

# 计算长度
length = modulo(v)  # 5.0 (sqrt(3² + 4² + 0²))

# 计算长度平方
length_squared = moduloSqrt(v)  # 25.0

# 归一化
unit_v = normalize(v)  # (0.6, 0.8, 0.0)

# 限制长度在 2 到 10 之间
clamped_v = clamp(v, 2, 10)  # 长度在 2 到 10 之间
```

### 3. 向量插值

```python
from ..architect.math.vec3 import vec, lerp, nlerp
import math

# 创建向量
start = vec((1, 0, 0))
end = vec((0, 1, 0))

# 线性插值
mid = lerp(start, end, 0.5)  # (0.5, 0.5, 0)

# 归一化插值（用于方向插值）
start_dir = normalize(vec((1, 0, 0)))
end_dir = normalize(vec((0, 1, 0)))
smooth_dir = nlerp(start_dir, end_dir, 0.5)  # 单位向量，方向在两者之间
```

### 4. 物理模拟

```python
from ..architect.math.vec3 import vec, add, mul, normalize, modulo
from ..architect.math.unit import time

class Projectile:
    def __init__(self, position, velocity, gravity=vec((0, -9.8, 0))):
        self.position = position
        self.velocity = velocity
        self.gravity = gravity
    
    def update(self, delta_time):
        # 应用重力
        self.velocity = add(self.velocity, mul(self.gravity, delta_time))
        
        # 更新位置
        self.position = add(self.position, mul(self.velocity, delta_time))
        
        # 检查地面碰撞（简单示例）
        if self.position.y < 0:
            self.position.y = 0
            # 反弹（能量损失）
            self.velocity.y = -self.velocity.y * 0.7
    
    def get_speed(self):
        """获取当前速度大小"""
        return modulo(self.velocity)
```

### 5. 3D 游戏中的方向计算

```python
from ..architect.math.vec3 import vec, normalize, cross, dot
import math

def look_at_direction(current_pos, target_pos, up=vec((0, 1, 0))):
    """计算从当前位置看向目标位置的方向"""
    # 计算看向方向
    direction = normalize(vec(target_pos) - vec(current_pos))
    
    # 计算右方向（与上和方向垂直）
    right = normalize(cross(up, direction))
    
    # 重新计算上方向（确保正交）
    new_up = cross(direction, right)
    
    return direction, right, new_up

def angle_between_vectors(a, b):
    """计算两个向量之间的角度（弧度）"""
    dot_product = dot(a, b)
    len_a = modulo(a)
    len_b = modulo(b)
    
    # 避免除以零
    if len_a == 0 or len_b == 0:
        return 0
    
    # 计算余弦值并限制在 [-1, 1] 范围内
    cos_angle = max(-1, min(1, dot_product / (len_a * len_b)))
    
    return math.acos(cos_angle)
```

## 注意事项

1. **零向量**: 对零向量进行归一化会返回零向量。
2. **精度**: 浮点数运算可能存在精度误差。
3. **性能**: 这些函数封装了 Minecraft 的 `Vector3` 类，性能较好。
4. **叉积顺序**: 叉积不满足交换律，`cross(a, b) = -cross(b, a)`。
5. **插值**: `nlerp` 是 `slerp`（球面线性插值）的近似，对于小角度插值效果较好。
6. **长度比较**: `compare` 函数比较的是长度的平方，避免开方运算。
