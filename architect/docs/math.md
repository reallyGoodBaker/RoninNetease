# 数学工具 (architect.math)

提供向量、矩阵运算及空间检测等 3D 数学工具。

## 向量运算 (vec3)

`architect.math.vec3` 封装了 `Vector3` 类及相关操作：

```python
from architect.math.vec3 import *

# 创建向量
v = vec((1, 2, 3))           # 从元组创建
v = vec(1.0, 2.0, 3.0)       # 从浮点数创建
v = vec()                     # 零向量 (0, 0, 0)
v = vec(otherVector)          # 从已有向量复制

# 基础运算
add(a, b)       # 加法
sub(a, b)       # 减法
mul(a, scalar)  # 标量乘法
div(a, scalar)  # 标量除法

# 向量运算
dot(a, b)       # 点积
cross(a, b)     # 叉积
modulo(a)       # 长度
moduloSqrt(a)   # 长度平方
normalize(a)    # 单位化

# 比较
compare(a, b)   # 返回长度平方差，大于0表示a > b

# 限制与插值
clamp(v, min, max)  # 限制向量长度在[min, max]内
lerp(a, b, t)       # 线性插值：a * (1-t) + b * t
nlerp(a, b, t)      # 单位化线性插值（a,b应为单位向量）

# 转换
tup(v)  # 转换为 (x, y, z) 元组
```

## 矩阵运算 (mat4)

提供 4x4 矩阵运算，常用于 3D 空间变换：

```python
from architect.math.mat4 import *

# 创建矩阵
identity()                              # 单位矩阵
lookAt(eye, target, up)                 # 观察矩阵（右手系，相机看向 -Z）
perspective(fov_degrees, aspect, near, far) # 透视投影矩阵

# 变换矩阵
translate(v)           # 平移矩阵
rotateAxis(axis, angle) # 绕任意轴旋转（弧度）
rotateX(angle)         # 绕 X 轴旋转
rotateY(angle)         # 绕 Y 轴旋转
rotateZ(angle)         # 绕 Z 轴旋转
rotateXYZ(roll, yaw, pitch)  # 按 ZYX 顺序旋转
scale(s)               # 缩放矩阵
transform(m, t, r, s)  # 组合变换：M_parent * T * R * S

# 矩阵运算
multiply(a, b)   # 矩阵乘法
transpose(m)     # 转置
inverse(m)       # 逆矩阵

# 点/向量变换
transformPoint(m, point)   # 变换点（包含平移）
transformVector(m, vector) # 变换向量（忽略平移）

# 坐标空间转换
localToWorld(modelMatrix, localPoint)  # 局部 → 世界
worldToLocal(modelMatrix, worldPoint)  # 世界 → 局部
worldToScreen(modelMatrix, viewMatrix, projectionMatrix, viewport, worldPoint)  # 世界 → 屏幕
```

## 空间工具 (math.utils)

```python
from architect.math.utils import *

# 屏幕和摄像机
screenSize()                                            # 获取屏幕尺寸
localViewMatrix()                                       # 获取当前摄像机视图矩阵
localProjectionMatrix()                                 # 获取当前投影矩阵
worldPosToScreenPos(worldPoint)                         # 世界坐标 → 屏幕坐标
screenToWorld(modelMatrix, screenPoint, filterType)     # 屏幕坐标 → 世界坐标（射线检测）

# 实体方向
forward(entityId, dist=1)   # 获取实体的水平前方方向
facing(entityId)             # 获取实体的完整前方方向（含俯仰）

# 范围检测
around(entityId, radius)    # 获取周围实体 ID 列表

# 方体碰撞检测
boxOverlap3dClient(pos, rot, size, debug=False)    # 以坐标原点为中心的方体重叠检测
boxOverlap3dForward(entityId, size, debug=False)    # 以实体前方为中心的方体检测
boxOverlap3dFacing(entityId, size, debug=False)     # 以实体朝向为中心的方体检测

# AABB 检测
pointInBox(point, size)         # 判断点是否在盒子内（盒子以原点为中心）
pointInAabb(point, min, max)    # 判断点是否在 AABB 内

# 实体 AABB
entityAabbDef(entityId)    # 获取实体的包围盒（基于 Molang）

# 默认过滤器
defaultFilters  # 预定义的实体过滤器（包含 player 和 mob）