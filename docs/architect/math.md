# `architect.math` 模块

数学工具集合，包含向量、矩阵、双精度数等工具：

- `vec3.py`, `mat4.py`, `double.py`, `utils.py`, `utilsServer.py`

用于空间运算、变换矩阵和常用数值工具。

详细函数/方法索引：

`vec3.py`:
- `vec(tup)` — 构造 Vector3
- `add(a, b)`, `sub(a, b)`, `mul(a, b)`, `div(a, b)` — 向量算术运算
- `dot(a, b)`, `cross(a, b)` — 点乘与叉乘
- `modulo(a)`, `moduloSqrt(a)` — 向量长度与长度平方
- `normalize(a)` — 单位化向量
- `compare(a, b)` — 比较两个向量的长度平方
- `clamp(v, min, max)` — 按长度限制向量
- `lerp(a, b, t)`, `nlerp(a, b, t)` — 线性/球面插值（归一化插值）

`mat4.py`:
- `identity()` — 单位矩阵
- `lookAt(eye, target, up)` — 视图矩阵
- `perspective(fov_degrees, aspect, near, far)` — 透视投影矩阵
- `multiply(a, b)`, `transpose(m)`, `inverse(m)` — 矩阵运算
- `translate(v)`, `rotateAxis(axis, angle)`, `rotateX/Y/Z(angle)`, `rotateXYZ(roll, yaw, pitch)`, `scale(s)` — 变换矩阵构造
- `transform(m, t, r, s)` — 构建模型变换矩阵
- `transformPoint(m, point)`, `transformVector(m, vector)` — 矩阵作用于点/向量
- `localToWorld`, `worldToLocal`, `worldToScreen`, `screenToWorld` — 常用坐标系转换工具

`utils.py`:
- `localViewMatrix()` / `localProjectionMatrix()` — 基于当前相机构建视图/投影矩阵
- `worldPosToScreenPos(worldPoint)` / `screenPosToWorldPos(screenPoint, depth)` — 坐标系转换快捷方法
- `pointInBox(point, box)` — 点在轴对齐盒子内判定
- `boxOverlap3dClient(pos, rot, size)` / `boxOverlap3dForward(entityId, size)` — 客户端的盒体重叠检测
- `forward(entityId)` — 获取实体朝向向量

`double.py`:
- `lerp(a, b, t)` — 双精度 lerp
- `clamp(x, min, max)` — 截断函数
- `smoothstep(edge0, edge1, x)` — 平滑插值函数

说明：以上函数依赖引擎或项目内的 `Vector3` / `Matrix` 类型，文档仅列出接口与用途。详见源码以获取更多实现细节。
