# Math — 数学库

RoninNetease 数学库提供了三维向量、四维向量、4×4 矩阵、插值工具、时间常量以及客户端/服务端的碰撞检测工具。所有 API 以**模块级函数**形式导出，底层使用网易引擎 SDK 的 `Vector3` 和 `Matrix` 类型。

---

## 1. 模块结构

```
architect.math
├── vec3.py      ← Vector3 三维向量运算（30+ 函数）
├── vec4.py      ← Vector4 四维齐次坐标
├── mat4.py      ← 4×4 变换矩阵（右手系，行向量左乘）
├── double.py    ← 标量插值与截断、常量（inf, epsilon）
├── unit.py      ← time 时间常量类
├── common.py    ← 汇总导出（vec3 + mat4 + double + unit）
├── utils.py     ← 客户端工具（屏幕转换、射线、碰撞检测）
└── utilsServer.py ← 服务端工具（碰撞检测、实体查询）
```

`common.py` 聚合导出了 `vec3.*`、`mat4`、`double.*` 和 `unit.*`，一行导入即可使用所有基础数学函数：

```python
from architect.math.common import *
```

---

## 2. 向量运算 — `vec3.py`

底层使用引擎 SDK 的 `Vector3` 类型。所有函数操作 `Vector3` 对象。

### 2.1 构造与转换

```python
from architect.math.vec3 import vec, tup

v = vec()                    # Vector3(0, 0, 0)
v = vec((1.0, 2.0, 3.0))    # 从 tuple 创建
v = vec(1.0, 2.0, 3.0)      # 从三个 float 创建
v = vec(someObject)          # 从有 .x/.y/.z 属性的对象创建（如 Vector4）
t = tup(v)                   # Vector3 → (x, y, z) tuple
```

`vec()` 支持 4 种输入类型：无参（零向量）、`float, float, float`、`tuple`、以及任何有 `x/y/z` 属性的对象。

### 2.2 四则运算

```python
from architect.math.vec3 import add, sub, mul, div

add(v1, v2)    # v1 + v2（返回 Vector3）
sub(v1, v2)    # v1 - v2
mul(v, 2.0)    # v * 2.0（标量乘）
div(v, 2.0)    # v / 2.0（标量除）
```

Vector3 原生支持 `+` `-` `*` `/` 运算符，这些包装函数直接使用引擎底层实现。

### 2.3 向量代数

```python
from architect.math.vec3 import dot, cross, modulo, moduloSqrt, normalize

dot(v1, v2)          # 点积（返回 float）
cross(v1, v2)        # 叉积 Vector3.Cross(a, b)
modulo(v)            # 向量长度 Vector3.Length(a)
moduloSqrt(v)        # 长度平方 Vector3.LengthSquared(a)
normalize(v)         # 单位化 Vector3.Normalized(a)
```

### 2.4 插值与钳制

```python
from architect.math.vec3 import lerp, nlerp, clamp, compare, vabs

lerp(a, b, t)        # 线性插值 a*(1-t) + b*t（t ∈ [0, 1]）
nlerp(a, b, t)       # 归一化线性插值（a、b 需为单位向量）

clamp(v, min, max)   # 将向量长度限制在 [min_len, max_len]
                     # len < min → 拉伸到 min
                     # len > max → 截断到 max

compare(a, b)        # 比较长度平方：>0 表示 |a| > |b|，<0 表示 |a| < |b|，=0 表示相等
vabs(v)              # 各分量取绝对值 Vector3(abs(x), abs(y), abs(z))
```

**`clamp` 实现细节：**

```python
def clamp(v, min, max):
    lenSqrt = Vector3.LengthSquared(v)
    if lenSqrt > max * max:
        return v * (max / math.sqrt(lenSqrt))   # 截断到 max 长度
    elif lenSqrt < min * min:
        return v * (min / math.sqrt(lenSqrt))   # 拉伸到 min 长度
    return v
```

---

## 3. 四维向量 — `vec4.py`

`Vector4` 是框架自定义的齐次坐标类，用于矩阵变换后的 4D 结果（如 `transformPoint` 返回 Vector4）。

### 3.1 构造

```python
from architect.math.vec4 import Vector4, vec4, tup4

v = vec4()                  # Vector4(0, 0, 0, 1.0)
v = vec4(1.0, 2.0, 3.0)    # Vector4(1, 2, 3, 1.0)
v = vec4(1.0, 2.0, 3.0, 0.5)  # Vector4(1, 2, 3, 0.5)
v = vec4((1.0, 2.0, 3.0))  # 从 tuple
v = vec4(someVector3)       # 从 Vector3 提升（w=1.0）
v = vec4(existingVector4)   # 直通原样返回

t = tup4(v)                 # (x, y, z, w)
```

### 3.2 运算

```python
from architect.math.vec4 import Vector4

a = Vector4(1, 2, 3, 1)
b = Vector4(0, 0, 0, 1)

c = a + b        # 分量加法
d = a - b        # 分量减法
e = a * 2.0      # 标量乘（各分量乘）
f = a * b        # 分量乘（Hadamard 积）
g = a / 2.0      # 标量除
```

### 3.3 与 Vector3 互转

```python
from architect.math.vec3 import vec

# Vector4 → Vector3（丢弃 w 分量）
v3 = vec(someVector4)

# Vector3 → Vector4（w 自动设为 1.0）
v4 = vec4(someVector3)
```

---

## 4. 矩阵函数 — `mat4.py`

操作引擎 SDK 的 `Matrix` 对象（4×4 矩阵，**行向量左乘**：`v' = v * M`），右手坐标系（摄像机看向 -Z 方向）。

### 4.1 基础矩阵

```python
from architect.math.mat4 import identity, translate, scale, rotateX, rotateY, rotateZ, rotateAxis, rotateXYZ

identity()                        # 4×4 单位矩阵

translate(vec((x, y, z)))         # 平移矩阵
scale(vec((sx, sy, sz)))          # 缩放矩阵

rotateX(angle)                    # 绕 X 轴旋转（弧度）
rotateY(angle)                    # 绕 Y 轴旋转（弧度）
rotateZ(angle)                    # 绕 Z 轴旋转（弧度）
rotateAxis(axis_vec, angle)       # 绕任意轴旋转（Rodrigues 公式）
rotateXYZ(rz, ry, rx)             # 组合旋转：rotateZ * rotateY * rotateX
```

**`rotateXYZ` 旋转顺序：** 先绕 Z、再绕 Y、最后绕 X（矩阵乘法从右到左应用）。参数名 `(roll, yaw, pitch)` 对应 `(z 旋转, y 旋转, x 旋转)`。

**`rotateX` / `rotateY` 的符号约定：**

```python
# rotateX: 绕 X 轴逆时针（从 +X 看向 -X 方向）
# 注意 Y 分量使用 -s（sin 取负），这是右手坐标系的标准
| 1   0   0   0 |
| 0   c  -s   0 |
| 0   s   c   0 |
| 0   0   0   1 |

# rotateY: 绕 Y 轴逆时针（从 +Y 看向 -Y 方向）  
# 注意 Z 分量使用 -s
| c   0   s   0 |
| 0   1   0   0 |
| -s  0   c   0 |
| 0   0   0   1 |
```

### 4.2 观察与投影矩阵

```python
from architect.math.mat4 import lookAt, perspective

lookAt(eye, target, up)
# 右手系观察矩阵，摄像机看向 -Z 方向
# eye: 摄像机位置 (Vector3)
# target: 目标点 (Vector3)
# up: 上方向 (Vector3)，通常为 vec((0, 1, 0))

perspective(fov_degrees, aspect, near, far)
# 右手系透视投影矩阵
# fov_degrees: 垂直视场角（角度制）
# aspect: 宽高比 (width / height)
# near/far: 近/远裁剪面
# NDC z 范围映射到 [-1, 1]
```

### 4.3 矩阵运算

```python
from architect.math.mat4 import multiply, transpose, inverse

multiply(a, b)     # a * b（使用 Matrix.matrix4_multiply）
transpose(m)       # 转置（m.Transpose()）
inverse(m)         # 逆矩阵（m.Inverse()）
```

### 4.4 变换

```python
from architect.math.mat4 import transform, transformPoint, transformVector, localToWorld, worldToLocal

# 标准模型变换：M_final = M_parent * T * R * S
transform(m, translate_vec, rotate_vec, scale_vec)
# m: 父矩阵（通常为 identity()）
# translate_vec: 平移 Vector3
# rotate_vec: 旋转 Vector3（分量 = z/y/x 弧度）
# scale_vec: 缩放 Vector3

# 用矩阵变换点（w=1，含平移）
transformPoint(mat, point)        # 返回 Vector4

# 用矩阵变换向量（w=0，忽略平移）
transformVector(mat, vector)      # 返回 Vector3

# 坐标空间转换
localToWorld(modelMatrix, localPoint)   # 模型空间 → 世界空间
worldToLocal(modelMatrix, worldPoint)   # 世界空间 → 模型空间
```

**`transformPoint` 与 `transformVector` 源码对比：**

```python
# transformPoint 手动做 m * [x, y, z, 1]^T
rx = m[0,0]*x + m[0,1]*y + m[0,2]*z + m[0,3]*1  # ← w=1，平移生效

# transformVector 手动做 m * [x, y, z, 0]^T
rx = m[0,0]*x + m[0,1]*y + m[0,2]*z             # ← w=0，平移被忽略
```

### 4.5 屏幕坐标转换

```python
from architect.math.mat4 import worldToScreen

screenPoint = worldToScreen(modelMatrix, viewMatrix, projMatrix, viewport, worldPoint)
# modelMatrix: 模型 → 世界矩阵
# viewMatrix: 世界 → 视图（lookAt 结果）
# projMatrix: 视图 → 投影（perspective 结果）
# viewport: (width, height) 窗口尺寸
# 返回 Vector3，x/y 为屏幕坐标，z 为深度
```

内部使用 `mvpMatrix = projection * view * model`，经过透视除法后映射到屏幕坐标系。

---

## 5. 插值与常量 — `double.py`

```python
from architect.math.double import lerp, clamp, smoothstep, alerp, inf, epsilon

lerp(a, b, t)           # 线性插值 a*(1-t) + b*t
clamp(x, min, max)      # 截断到 [min, max]
smoothstep(e0, e1, x)   # 平滑阶梯 t^2(3-2t)，t = clamp((x-e0)/(e1-e0), 0, 1)
alerp(start, end, t)    # 角度线性插值（自动处理 0°/360° 环绕）

inf   = 1e+10           # 大数常量
epsilon = 1e-8          # 浮点精度常量
```

### 5.1 `alerp` — 角度插值

对角度值进行线性插值，自动选择最短路径处理 0°/360° 的环绕问题：

```python
from architect.math.double import alerp

alerp(350.0, 10.0, 0.5)   # 0.0  (即 360°/0°，走 20° 短路径，而非 340° 长路径)
alerp(10.0, 350.0, 0.5)   # 0.0
alerp(10.0, 100.0, 0.5)   # 55.0

# 内部实现
diff = (end - start) % 360.0
if diff > 180.0:   diff -= 360.0
elif diff < -180.0: diff += 360.0
return start + diff * t
```

### 5.2 `smoothstep` — 平滑曲线

```python
smoothstep(0.0, 1.0, 0.5)  # 0.5（中间值不变）
smoothstep(0.0, 1.0, 0.25) # 约 0.156（靠近边缘时减速）

# 典型用途：动画缓入缓出
t = smoothstep(0.0, duration, elapsed)
alpha = lerp(fromVal, toVal, t)
```

---

## 6. 时间常量 — `unit.py`

```python
from architect.math.unit import time

time.entityTick   # 0.05 秒（实体 Tick 间隔）
time.tick         # ~0.033 秒（30fps Tick 间隔）
time.ms           # 0.001 秒
time.s            # 1 秒
time.m            # 60 秒
time.h            # 3600 秒
time.d            # 86400 秒
time.w            # 604800 秒
time.y            # 31536000 秒
```

用法：`time.s * 3` 表示 3 秒，`time.ms * 500` 表示 500 毫秒。

---

## 7. 客户端工具 — `math/utils.py`

### 7.1 屏幕坐标工具

```python
from architect.math.utils import screenSize, localViewMatrix, localProjectionMatrix, worldPosToScreenPos, screenToWorld

w, h = screenSize()          # 获取窗口尺寸

view = localViewMatrix()     # 从摄像机位置和朝向构建 lookAt 矩阵
proj = localProjectionMatrix()  # 从 fov 和宽高比构建 perspective 矩阵

screenPoint = worldPosToScreenPos(worldPoint)
# 世界坐标 → 屏幕坐标（内部调用 worldToScreen）

worldPoint = screenToWorld(modelMatrix, screenPoint, filterType, debug)
# 屏幕坐标 → 世界坐标（射线拾取）
# modelMatrix: 模型矩阵（通常 identity()）
# screenPoint: 屏幕点 Vector3（x, y 为屏幕坐标，可忽略 z）
# filterType: RayFilterType.OnlyBlocks / .OnlyEntities 等
# debug=False: 设为 True 会绘制调试射线
# 返回 Vector3 世界坐标，或 None（未命中）
```

**`screenToWorld` 实现原理：** 将屏幕坐标通过逆 MVP 矩阵转换到世界空间，构建射线后用引擎 `getEntitiesOrBlockFromRay` 进行碰撞检测。

### 7.2 实体朝向与查询

```python
from architect.math.utils import forward, facing, around, entityAabbDef

# forward: 实体前方单位向量（忽略 Y 分量，水平方向）
dirVec = forward(entityId)      # 返回 Vector3
dirVec = forward(entityId, 5.0)  # 返回长度为 5 的单位方向向量

# facing: 实体完整朝向向量（含 Y 分量）
facingVec = facing(entityId)

# around: 查询半径内的实体 ID 列表（方形区域）
nearby = around(entityId, 10.0)  # 边长 20 的正方形区域

# entityAabbDef: 获取实体头部 AABB 包围盒（基于 Molang 骨骼查询）
(min_x, min_y, min_z), (max_x, max_y, max_z) = entityAabbDef(entityId)
# 内部通过 EvalMolangExpression("q.bone_aabb('head')") 获取
```

### 7.3 碰撞检测

```python
from architect.math.utils import boxOverlap3dClient, boxOverlap3dForward, boxOverlap3dFacing, boxOverlap3dBouding

# 任意位置和朝向的盒体碰撞检测
entities = boxOverlap3dClient(pos, rot, size, debug=False)
# pos: (x, y, z) 世界坐标
# rot: (yaw, pitch, roll) 弧度
# size: (width, height, depth) 盒体全尺寸

# 实体正前方的盒体碰撞（自动获取位置 + 朝向）
entities = boxOverlap3dForward(entityId, size, debug=False)
# size: (width, height, depth)，盒体中心在实体前方 zDist 处

# 实体朝向的盒体碰撞（使用 GetRot 获取旋转 + 位置）
entities = boxOverlap3dFacing(entityId, size, debug=False)

# 自定义起终点包围盒检测
entities = boxOverlap3dBouding(start, end, forward, debug=False)
# start/end: (x, y, z) 世界坐标（包围盒的两个对角点）
# forward: (x, y, z) 朝向单位向量
```

### 7.4 包围盒点测试

```python
from architect.math.utils import pointInBox, pointInAabb

inside = pointInBox(point, size)
# point: (x, y, z) tuple
# size: (width, height, depth) 全尺寸
# 盒体以原点为中心，范围 [-size/2, size/2]

inside = pointInAabb(point, min_vec, max_vec)
# 轴对齐包围盒，范围 [min, max]
```

### 7.5 默认过滤器

```python
from architect.math.utils import defaultFilters

# 射线投射默认过滤器：只命中 player 和 mob
defaultFilters = {
    "any_of": [
        {"subject": "other", "test": "is_family", "value": "player"},
        {"subject": "other", "test": "is_family", "value": "mob"}
    ]
}
```

---

## 8. 服务端工具 — `math/utilsServer.py`

### 8.1 碰撞检测

```python
from architect.math.utilsServer import boxOverlap3dServer, boxOverlap3dForward

# 服务端盒体碰撞（使用 Location 而非 tuple）
entities = boxOverlap3dServer(location, rot, size)
# location: Location(pos=(x,y,z), dim=dimId)
# rot: (yaw, pitch, roll) 弧度
# size: (width, height, depth)

# 实体正前方碰撞（自动获取位置 + 朝向 + 维度）
entities = boxOverlap3dForward(entityId, size)
```

### 8.2 实体查询

```python
from architect.math.utilsServer import forward, facing, around

dirVec = forward(entityId)      # 实体前方单位向量（水平方向）
dirVec = forward(entityId, 5.0)  # 长度 5

facingVec = facing(entityId)     # 完整朝向（含 Y 分量）

nearby = around(location, radius)  # 以 Location 为中心查询方形区域实体
```

### 8.3 包围盒测试

```python
from architect.math.utilsServer import pointInBox

inside = pointInBox(point, size)
# 与客户端版本的 pointInBox 签名相同
```

---

## 9. 完整示例

### 9.1 近战攻击检测

```python
from architect.math.vec3 import vec, tup, normalize
from architect.math.utils import boxOverlap3dForward, forward

class CombatSystem(ClientSubsystem):
    ATTACK_SIZE = (2, 3, 2)  # (宽, 高, 深)

    def tryAttack(self):
        hits = boxOverlap3dForward(self.entityId, self.ATTACK_SIZE)
        for targetId in hits:
            self.doDamage(targetId)
```

### 9.2 摄像机追踪（利用矩阵坐标转换）

```python
from architect.math.vec3 import vec, normalize, add, sub, modulo
from architect.math.mat4 import lookAt, perspective, WorldToScreen
from architect.math.double import clamp, smoothstep
from architect.math.unit import time

class CameraTrack(ClientSubsystem):
    def trackTarget(self, targetPos, elapsed):
        camPos = vec(self.camera.GetPosition())
        forward = normalize(sub(targetPos, camPos))
        dist = modulo(sub(targetPos, camPos))

        # 平滑变焦
        t = clamp(elapsed / (2 * time.s), 0.0, 1.0)
        desiredFov = 30.0 + (dist * 2)
        currentFov = 60.0 + (desiredFov - 60.0) * smoothstep(0.0, 1.0, t)
        return currentFov
```

### 9.3 世界坐标 → 屏幕坐标（HUD 绘制）

```python
from architect.math.mat4 import identity, worldToScreen
from architect.math.utils import localViewMatrix, localProjectionMatrix, screenSize
from architect.math.vec3 import vec

w, h = screenSize()
screenPt = worldToScreen(
    identity(),
    localViewMatrix(),
    localProjectionMatrix(),
    (w, h),
    vec(entityPos)
)

# screenPt.x / screenPt.y 即为屏幕像素坐标
# screenPt.z 为深度值（可用于深度排序）
```

### 9.4 分帧平滑旋转（alerp 防止 360° 跳变）

```python
from architect.math.double import alerp

class SmoothRotation(ClientSubsystem):
    def updateRotation(self, targetAngle):
        self.currentAngle = alerp(self.currentAngle, targetAngle, 0.1)
        # 0.1 的 t 值 = 指数衰减，每帧靠近 10%
        # alerp 自动选择最短路径，避免 350° → 10° 时旋转 340°
```

---

## 下一步

- [Molang 操作参考 (molang.md)](molang.md) — Molang 变量读写
- [实体预设 (persona.md)](persona.md) — 玩家模型与外观
- [最佳实践 (best-practices.md)](best-practices.md) — 开发建议