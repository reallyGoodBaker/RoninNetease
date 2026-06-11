# Math — 数学库

RoninNetease 数学库提供了三维向量（`vec3`、`vec4`）、4×4 矩阵（`mat4`）、高精度浮点数（`Double`）和常用几何工具。

---

## 1. 概述

```
architect.math
├── vec3.py     ← Vec3 三维向量
├── vec4.py     ← Vec4 四维向量
├── mat4.py     ← Mat4 4×4 变换矩阵
├── double.py   ← Double 高精度浮点运算
├── common.py   ← 通用工具（距离、插值等）
├── unity.py    ← Unity 引擎相关类型
├── utils.py    ← Vec3Utils 客户端工具
└── utilsServer.py ← 服务端工具
```

---

## 2. Vec3 — 三维向量

### 2.1 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `x` | `float` | X 分量 |
| `y` | `float` | Y 分量 |
| `z` | `float` | Z 分量 |

### 2.2 构造与基本操作

```python
from architect.math.vec3 import Vec3

# 构造
v = Vec3(1.0, 2.0, 3.0)
zero = Vec3.zero()          # (0, 0, 0)
one = Vec3.one()            # (1, 1, 1)
up = Vec3.up()              # (0, 1, 0)
forward = Vec3.forward()    # (0, 0, 1)

# 读写
x = v.x
v.x = 10.0

# 运算
v3 = v + Vec3(1, 2, 3)     # 加法
v3 = v - Vec3(1, 2, 3)     # 减法
v3 = v * 2.0                # 标量乘
v3 = v / 2.0                # 标量除
```

### 2.3 Vec3Utils — 客户端

```python
from architect.math.utils import Vec3Utils

# 距离
dist = Vec3Utils.distance(v1, v2)           # 两点距离
sqr_dist = Vec3Utils.distance_squared(v1, v2) # 距离平方

# 方向与角度
direction = Vec3Utils.direction(v1, v2)     # 单位方向向量
angle = Vec3Utils.angle(v1, v2)            # 两向量夹角（弧度）
angle_deg = Vec3Utils.angle_degrees(v1, v2) # 两向量夹角（度）

# 单位化与长度
norm = Vec3Utils.normalize(v)               # 单位化
length = Vec3Utils.magnitude(v)             # 向量长度
sqr_len = Vec3Utils.magnitude_squared(v)    # 长度平方

# 线性插值
lerped = Vec3Utils.lerp(v1, v2, t)         # 线性插值 t ∈ [0, 1]

# 点积与叉积
dot = Vec3Utils.dot(v1, v2)                # 点积
cross = Vec3Utils.cross(v1, v2)            # 叉积

# 旋转
rotated = Vec3Utils.rotate(v, axis, angle)  # 绕轴旋转

# 投影
proj = Vec3Utils.project(v, onto)           # 投影到 onto 方向
rej = Vec3Utils.reject(v, onto)             # 正交于 onto 的分量

# 反射
reflected = Vec3Utils.reflect(v, normal)     # 反射向量
```

### 2.4 服务端

```python
from architect.math.utilsServer import Vec3UtilsServer

# 服务端也有类似的 Vec3 工具集
```

---

## 3. Vec4 — 四维向量

```python
from architect.math.vec4 import Vec4

v = Vec4(1.0, 2.0, 3.0, 1.0)

x = v.x     # 1.0
y = v.y     # 2.0
z = v.z     # 3.0
w = v.w     # 1.0
```

常用于：
- 齐次坐标 `(x, y, z, 1)` — 表示位置
- 齐次坐标 `(x, y, z, 0)` — 表示方向
- RGBA 颜色 `(r, g, b, a)`

---

## 4. Mat4 — 4×4 变换矩阵

```python
from architect.math.mat4 import Mat4

# 构造
identity = Mat4.identity()              # 单位矩阵
translation = Mat4.translation(v3)      # 平移矩阵
rotation = Mat4.rotation(axis, angle)   # 旋转矩阵
scale = Mat4.scale(v3)                  # 缩放矩阵

# 组合变换
transform = translation * rotation * scale

# 矩阵-向量乘法
result_vec4 = transform * Vec4(1, 0, 0, 1)
result_vec3 = transform * Vec3(1, 0, 0)  # 结果自动除 w
```

---

## 5. Double — 高精度浮点数

```python
from architect.math.double import Double

# 构造
d = Double(3.14159265358979)
d = Double.long_value(314159265358979)
d = Double.int_value(3)

# 运算
sum_d = d + Double(1.0)
diff = d - Double(0.5)
prod = d * Double(2.0)
quot = d / Double(2.0)
```

`Double` 封装了底层的高精度定点数运算，用于需要精确计算的场景（如经济系统、物理模拟）。

---

## 6. 通用工具函数 — `math/common.py`

```python
from architect.math.common import (
    distance, distance_sq,
    lerp, lerp_vec3,
    clamp, clamp01,
    move_towards, move_towards_angle,
    get_rotation_from_direction
)

# 距离
d = distance(v1, v2)            # float
d2 = distance_sq(v1, v2)       # 距离平方

# 插值
val = lerp(0.0, 1.0, t)        # 标量插值
vec = lerp_vec3(v1, v2, t)     # Vec3 插值

# 截断
x = clamp(value, 0, 100)       # 限制在 [min, max]
x = clamp01(value)              # 限制在 [0, 1]

# 渐进移动
pos = move_towards(current, target, max_delta)
angle = move_towards_angle(current, target, max_delta)

# 方向转旋转
rot = get_rotation_from_direction(direction_vec3)
```

---

## 7. Unit — 单位转换

```python
from architect.math.unit import (
    degrees_to_radians,
    radians_to_degrees
)

rad = degrees_to_radians(90)    # π/2
deg = radians_to_degrees(3.14)  # ~180°
```

---

## 8. 完整示例

```python
from architect.math.vec3 import Vec3
from architect.math.mat4 import Mat4
from architect.math.utils import Vec3Utils

# 玩家朝向计算
player_pos = Vec3(0, 64, 0)
target_pos = Vec3(10, 64, 10)

# 计算方向
direction = Vec3Utils.direction(player_pos, target_pos)
# 结果近似: Vec3(0.707, 0, 0.707)

# 计算距离
dist = Vec3Utils.distance(player_pos, target_pos)
# 结果: ~14.14

# 创建变换矩阵
transform = Mat4.translation(player_pos) * \
            Mat4.rotation(Vec3.up(), Vec3Utils.angle(Vec3.forward(), direction))

# 插值相机平滑跟随
camera_pos = Vec3Utils.lerp(current_cam, target_cam, 0.1)

# 反射弹道
bullet_dir = Vec3(1, 0, 0)
surface_normal = Vec3(-1, 1, 0)
reflected = Vec3Utils.reflect(bullet_dir, Vec3Utils.normalize(surface_normal))
```

---

## 下一步

- [工具集 (utils.md)](utils.md) — 其他工具模块
- [最佳实践 (best-practices.md)](best-practices.md) — 开发建议