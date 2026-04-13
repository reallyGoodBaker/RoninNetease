# 常用工具与扩展 (Utils)

`architect` 提供了丰富的辅助模块，涵盖数学运算、引擎组件封装、状态机等。

## 数学工具 (architect.math)

### 向量运算 (vec3)
`architect.math.vec3` 封装了 `Vector3` 类及相关操作：
- `vec(tuple)`: 创建一个向量对象。
- `add(a, b)`, `sub(a, b)`, `mul(a, num)`, `div(a, num)`: 基础四则运算。
- `dot(a, b)`, `cross(a, b)`: 点积与叉积。
- `modulo(a)`, `moduloSqrt(a)`: 获取长度与长度平方。
- `normalize(a)`: 单位化。
- `clamp(v, min, max)`: 限制向量长度在指定范围内。
- `lerp(a, b, t)`, `nlerp(a, b, t)`: 线性插值与单位化插值。
- `tup(v)`: 将向量转换为元组。

### 矩阵运算 (mat4)
提供 4x4 矩阵运算，常用于 3D 空间变换。

## 引擎组件封装 (architect.level)

通过 `LevelServer` 和 `LevelClient` 类，可以静态访问预创建好的引擎组件。

### LevelServer (服务端)
直接通过属性访问常用的服务端组件：
- `game`, `chunkSource`, `achievement`, `biome`, `dimension`, `blockInfo`, `weather`, `time`, `block`, `blockEntity`, `blockEntityData`, `blockState`, `message`, `command`, `chestBlock`, `explosion`, `extraData`, `feature`, `itemBanned`, `mobSpawn`, `projectile`, `portal`, `recipe`, `redstone`。

### LevelClient (客户端)
通过 `LevelClient.getInstance()` 获取实例并访问组件：
- `localPlayer`, `achievement`, `actorRender`, `biome`, `block`, `blockInfo`, `camera`, `configClient`, `customAudio`, `dimension`, `drawing`, `fog`, `game`, `model`, `neteaseShop`, `operation`, `playerView`, `postProcess`, `recipe`, `skyRender`, `textBoard`, `textNotify`, `item`, `neteaseWindow`。

## 状态机 (architect.fsm)

提供了一套标准的有限状态机框架，适用于处理实体的 AI 状态切换（如：空闲、寻路、攻击）或复杂的任务阶段控制。

## 动画与效果 (architect.utils)

- **animFader**: 用于处理属性值的平滑淡入淡出（如音量、亮度、透明度）。
- **molang**: 提供 `architect.utils.molang.client/server` 接口，方便在代码中快速设置实体的 Molang 变量或查询变量。
- **persona**: 皮肤形象相关的工具集。
- **device**: 获取客户端运行环境信息。

## 数据持久化 (architect.persistent)

`architect.persistent` 模块支持将组件数据自动同步至服务端的持久化存储，或者客户端的本地存储。结合 `@Component(persist=True)` 使用，可以极大简化数据保存逻辑。
