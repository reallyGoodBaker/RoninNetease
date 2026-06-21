# Math — 数学库

RoninNetease 数学库提供了三维向量、4×4 矩阵、几何工具和物理时间常量。所有 API 以**模块级函数**形式导出。

---

## 1. 概述

```
architect.math
├── vec3.py      ← 三维向量运算函数
├── vec4.py      ← Vec4 四维向量
├── mat4.py      ← 4×4 变换矩阵函数
├── double.py    ← 插值与截断函数、常量（inf, epsilon）
├── common.py    ← 汇总导出（vec3 + mat4 + double + unit）
├── unit.py      ← time 时间常量类
├── utils.py     ← 客户端工具（屏幕转换、碰撞检测、射线等）
└── utilsServer.py ← 服务端工具（碰撞检测、实体查询等）
```

---

## 2. 向量运算函数 — `vec3.py`

所有函数操作 `Vector3` 对象（引擎 SDK 提供），框架只导出包装函数：

### 2.1 构造与转换

```python
from architect.math.vec3 import vec, tup

v = vec((1.0, 2.0, 3.0))  # 从元组创建 Vector3
v = vec(1.0, 2.0, 3.0)    # 从三个浮点数创建
t = tup(v)                  # Vector3 → tuple
```

### 2.2 运算

```python
from architect.math.vec3 import add, sub, mul, div, dot, cross, modulo, moduloSqrt, normalize, lerp, nlerp

add(v1, v2)        # 加法
sub(v1, v2)        # 减法
mul(v, 2.0)        # 标量乘
div(v, 2.0)        # 标量除
dot(v1, v2)        # 点积（返回 float）
cross(v1, v2)      # 叉积（返回 Vector3）
modulo(v)          # 向量长度
moduloSqrt(v)      # 向量长度平方
normalize(v)       # 单位化
lerp(a, b, t)      # 线性插值 (t ∈ [0, 1])
nlerp(a, b, t)     # 归一化线性插值（两向量需为单位向量）
```

### 2.3 工具

```python
from architect.math.vec3 import clamp, compare, vabs

clamp(v, min_len, max_len)  # 将向量长度限制在 [min, max]
compare(a, b)                # 比较长度：>0 表示 a > b，<0 表示 a < b，0 表示相等
vabs(v)                      # 各分量取绝对值
```

---

## 3. 矩阵函数 — `mat4.py`

操作引擎 SDK 的 `Matrix` 对象（4x4 矩阵，行向量左乘：`v' = v * M`）：

### 3.1 基础矩阵

```python
from architect.math.mat4 import identity, translate, scale, rotateX, rotateY, rotateZ, rotateAxis, rotateXYZ

identity()                      # 单位矩阵
translate(vec((x, y, z)))      # 平移矩阵
scale(vec((sx, sy, sz)))       # 缩放矩阵
rotateX(angle)                  # 绕 X 轴旋转（弧度）
rotateY(angle)                  # 绕 Y 轴旋转（弧度）
rotateZ(angle)                  # 绕 Z 轴旋转（弧度）
rotateAxis(axis_vec, angle)    # 绕任意轴旋转
rotateXYZ(rz, ry, rx)           # 组合旋转（先 Z，再 Y，最后 X）
```

### 3.2 观察与投影矩阵

```python
from architect.math.mat4 import lookAt, perspective

lookAt(eye, target, up)                       # 观察矩阵（右手系，-Z 为前）
perspective(fov_degrees, aspect, near, far)    # 透视投影矩阵
```

### 3.3 矩阵运算

```python
from architect.math.mat4 import multiply, transpose, inverse

multiply(a, b)   # 矩阵乘法
transpose(m)     # 转置
inverse(m)       # 逆矩阵
```

### 3.4 变换

```python
from architect.math.mat4 import transform, transformPoint, transformVector, localToWorld, worldToLocal

# 标准模型变换：先缩放(S)，再旋转(R)，最后平移(T)，再乘父矩阵(m)
transform(m, translate_vec, rotate_vec, scale_vec)

# 用矩阵变换点（含平移，w=1）
transformPoint(mat, point)     # 返回 Vector4

# 用矩阵变换向量（忽略平移，w=0）
transformVector(mat, vector)   # 返回 Vector3

# 坐标空间转换
localToWorld(modelMatrix, localPoint)   # 模型空间 → 世界空间
worldToLocal(modelMatrix, worldPoint)   # 世界空间 → 模型空间
```

### 3.5 屏幕坐标转换

```python
from architect.math.mat4 import worldToScreen

screenPoint = worldToScreen(modelMatrix, viewMatrix, projMatrix, viewport, worldPoint)
# 返回 Vector3，x/y 为屏幕坐标，z 为深度
```

---

## 4. 插值与常量 — `double.py`

```python
from architect.math.double import lerp, clamp, smoothstep, alerp, inf, epsilon

lerp(a, b, t)                          # 浮点线性插值
alerp(start, end, t)                   # 角度线性插值（自动处理 360° 环绕）
clamp(x, min_val, max_val)             # 截断到 [min, max]
smoothstep(edge0, edge1, x)            # 平滑阶梯函数
inf                                     # 1e+10
epsilon                                 # 1e-8
```

### 4.1 `alerp` — 角度线性插值

对角度值进行线性插值，自动选择最短路径处理 `0°` / `360°` 的环绕问题：

```python
from architect.math.double import alerp

# 插值 350° → 10° 会走 20° 的短路径，而非 340° 的长路径
alerp(350.0, 10.0, 0.5)   # 0.0 (即 360°/0°)
alerp(10.0, 350.0, 0.5)   # 0.0
alerp(10.0, 100.0, 0.5)   # 55.0
```

> `alerp` 适用于旋转角度、朝向、动画骨骼旋转等需要角度插值的场景。

---

## 5. 时间常量 — `unit.py`

```python
from architect.math.unit import time

time.entityTick   # 0.05 秒
time.tick         # ~0.033 秒（30fps）
time.ms           # 0.001 秒
time.s            # 1 秒
time.m            # 60 秒
time.h            # 3600 秒
time.d            # 86400 秒
time.w            # 604800 秒
time.y            # 31536000 秒
```

> 用 `time.s * 3` 表示 3 秒，`time.ms * 500` 表示 500 毫秒。

---

## 6. 客户端工具 — `math/utils.py`

### 6.1 屏幕坐标工具

```python
from architect.math.utils import (
    screenSize, localViewMatrix, localProjectionMatrix,
    worldPosToScreenPos, screenToWorld
)

w, h = screenSize()
view = localViewMatrix()
proj = localProjectionMatrix()
screenPoint = worldPosToScreenPos(worldPoint)
worldPoint = screenToWorld(modelMatrix, screenPoint)
```

### 6.2 实体查询与朝向

```python
from architect.math.utils import forward, facing, around, entityAabbDef

dirVec = forward(entityId)          # 实体前方单位向量
facingVec = facing(entityId)        # 实体朝向向量（含 Y 分量）
nearby = around(entityId, radius)   # 半径内实体 ID 列表
aabbMin, aabbMax = entityAabbDef(entityId)  # 实体 AABB 包围盒
```

### 6.3 碰撞检测

```python
from architect.math.utils import (
    boxOverlap3dClient, boxOverlap3dForward, boxOverlap3dFacing
)

entities = boxOverlap3dClient(pos, rot, size, debug=False)
entities = boxOverlap3dForward(entityId, size, debug=False)
entities = boxOverlap3dFacing(entityId, size, debug=False)
```

### 6.4 辅助函数

```python
from architect.math.utils import pointInBox, pointInAabb

inside = pointInBox(point, size)
inside = pointInAabb(point, min_vec, max_vec)
```

---

## 7. 服务端工具 — `math/utilsServer.py`

```python
from architect.math.utilsServer import (
    boxOverlap3dServer, boxOverlap3dForward, forward, facing, around, pointInBox
)

# 碰撞检测（服务端使用 Location + dimId）
entities = boxOverlap3dServer(location, rot, size)

# 实体前方
entities = boxOverlap3dForward(entityId, size)

# 朝向与附近实体
dirVec = forward(entityId)
nearby = around(location, radius)
```

---

## 8. 完整示例

```python
from architect.math.vec3 import vec, add, normalize, modulo, tup
from architect.math.mat4 import lookAt, perspective, worldToScreen
from architect.math.utils import forward, boxOverlap3dForward
from architect.math.double import clamp, smoothstep
from architect.math.unit import time

# 距离检测
player = vec((0, 64, 0))
target = vec((10, 64, 10))
dir_to_target = normalize(add(target, vec((0, 0, 0))))  # target - player 用 sub
dist = modulo(target - player)
if dist < 5.0:
    print('In range')

# 屏幕投影
view = lookAt(player, target, vec((0, 1, 0)))
proj = perspective(60.0, 16.0 / 9.0, 0.1, 100.0)
screenPt = worldToScreen(identity(), view, proj, (1920, 1080), target)

# 碰撞检测
hits = boxOverlap3dForward(entityId, (2, 3, 2))

# 平滑过渡（3 秒内完成）
t = clamp(current_time / (3 * time.s), 0.0, 1.0)
alpha = smoothstep(0.0, 1.0, t)
```

---

## 下一步

- [工具集 (utils.md)](utils.md) — 其他工具模块
- [最佳实践 (best-practices.md)](best-practices.md) — 开发建议