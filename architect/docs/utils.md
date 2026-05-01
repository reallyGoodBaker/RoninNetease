# 常用工具与扩展 (Utils)

`architect` 提供了丰富的辅助模块，涵盖数学运算、引擎组件封装、状态机、动画效果等。

## 数学工具 (architect.math)

### 向量运算 (vec3)

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

### 矩阵运算 (mat4)

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

### 空间工具 (math.utils)

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
```

## 引擎组件封装 (architect.level)

通过 `LevelServer` 和 `LevelClient` 类，静态访问预创建好的引擎组件。

### LevelServer（服务端）

```python
from architect.level.server import LevelServer

LevelServer.game               # 游戏组件
LevelServer.chunkSource        # 区块源
LevelServer.achievement        # 成就
LevelServer.biome              # 生物群系
LevelServer.dimension          # 维度
LevelServer.blockInfo          # 方块信息
LevelServer.weather            # 天气
LevelServer.time               # 时间
LevelServer.block              # 方块
LevelServer.blockEntity        # 方块实体
LevelServer.blockEntityData    # 方块实体数据
LevelServer.blockState         # 方块状态
LevelServer.blockUseEventWhiteList  # 方块使用事件白名单
LevelServer.message            # 消息
LevelServer.command            # 命令
LevelServer.chestBlock         # 箱子
LevelServer.explosion          # 爆炸
LevelServer.extraData          # 额外数据
LevelServer.feature            # 特征
LevelServer.itemBanned         # 禁用物品
LevelServer.mobSpawn           # 生物生成
LevelServer.projectile         # 抛射物
LevelServer.portal             # 传送门
LevelServer.recipe             # 配方
LevelServer.redstone           # 红石
```

### LevelClient（客户端）

```python
from architect.level.client import LevelClient

level = LevelClient.getInstance()

level.localPlayer              # 本地玩家
level.achievement              # 成就
level.actorRender              # 实体渲染
level.biome                    # 生物群系
level.block                    # 方块
level.blockGeometry            # 方块几何
level.blockInfo                # 方块信息
level.blockUseEventWhiteList   # 方块使用事件白名单
level.camera                   # 摄像机
level.chunkSource              # 区块源
level.configClient             # 客户端配置
level.customAudio              # 自定义音频
level.dimension                # 维度
level.drawing                  # 绘制
level.fog                      # 雾
level.game                     # 游戏
level.model                    # 模型
level.neteaseShop              # 网易商店
level.operation                # 操作
level.playerView               # 玩家视角
level.postProcess              # 后处理
level.recipe                   # 配方
level.skyRender                # 天空渲染
level.textBoard                # 文本板
level.textNotify               # 文本通知
level.virtualWorld             # 虚拟世界
level.item                     # 物品
level.neteaseWindow            # 网易窗口
```

## 绘图工具 (architect.utils.drawing)

提供游戏内调试用的 3D 线条绘制功能：

```python
from architect.math.vec3 import vec, Vector3
from architect.utils.drawing import drawLine, drawBox

# 绘制一条线（起点，终点，颜色，持续时间）
drawLine(
    vec((0, 0, 0)),
    vec((10, 0, 0)),
    vec((1, 0, 0)),  # 红色
    duration=5       # 5秒后自动消失
)

# 绘制一个方体框（中心，尺寸，前方方向，颜色，持续时间）
drawBox(
    vec((0, 5, 0)),      # 中心位置
    vec((2, 2, 2)),      # 尺寸 (width, height, depth)
    vec((1, 0, 0)),      # 前方方向
    vec((1, 1, 0)),      # 黄色
    duration=5
)
```

## 客户端工具 (architect.utils.client)

```python
from architect.utils.client import isPlayer

# 判断实体是否为玩家
if isPlayer(entityId):
    print('This is a player')
```

客户端子系统 `ClientUtilsSubsys` 自动注册了两个自定义事件监听器：
- `PlayCustomAudio`：播放自定义音效
- `StopCustomAudio`：停止自定义音效

## 状态机 (architect.fsm)

提供了一个经典的有限状态机框架（**不推荐**在 ECS 中使用，建议使用组件模式替代）。

### 定义状态

```python
from architect.fsm.deprecated import State, Fsm

class IdleState(State):
    def onEnter(self):
        print('Enter idle')

    def onExit(self):
        print('Exit idle')

    def onUpdate(self):
        # 每帧更新逻辑
        pass

    def onEvent(self, type, data):
        # 处理事件
        pass

class AttackState(State):
    def onEnter(self):
        print('Enter attack')
```

### 使用状态机

```python
# 创建状态机
fsm = Fsm(entityId, IdleState, name='ai')

# 添加状态
fsm.addState('attack', AttackState)
# 或批量添加
fsm.addStateMapping({
    'idle': IdleState,
    'attack': AttackState,
})

# 状态切换
fsm.transitionTo('attack')

# 每帧更新
fsm.callUpdate()
```

### State 内置实用方法

```python
class MyState(State):
    def onEnter(self):
        # 获取 FSM 宿主实体 ID
        self.entityId

        # 切换 MarkVariant（实体变体）
        self.markVariant(1)    # 设置
        variant = self.markVariant()  # 获取

        # 播放音效
        self.playSound('minecraft:entity.player.attack')

        # 控制实体移动权限
        self.movement(enabled=False)   # 禁用移动
        self.movement(enabled=True)    # 启用移动

        # 控制摄像机权限
        self.camera(enabled=False)     # 禁用摄像机控制
```

## 动画与效果

### Molang

```python
# 客户端设置 Molang 变量
from architect.utils.molang.client import setMolang, getMolang

setMolang(entityId, 'variable.my_var', 1.0)
value = getMolang(entityId, 'variable.my_var')

# 服务端设置 Molang 变量
from architect.utils.molang.server import setMolang, getMolang
```

### 动画淡入淡出

```python
from architect.utils.animFader import *

# 创建动画过渡效果
fader = createAnimFader(fromValue, toValue, duration)
```

## 设备信息 (architect.utils.device)

获取客户端运行环境信息：

```python
from architect.utils.device.client import *

# 获取设备信息
deviceInfo = getDeviceInfo()
```

## 皮肤形象 (architect.utils.persona)

```python
from architect.utils.persona.client import *
from architect.utils.persona.server import *

# 客户端/服务端的皮肤形象信息
```

## 数据持久化 (architect.persistent)

支持将组件数据同步至持久化存储。结合 `@Component(persist=True)` 使用：

```python
from architect.persistent.client import ClientKVDatabase, ClientKVDatabaseGlobal
from architect.persistent.server import ServerKVDatabase

# 服务端持久化数据库
db = ServerKVDatabase.getInstance()
db.setData('player_score', 100)
score = db.getData('player_score')

# 客户端本地持久化数据库
clientDb = ClientKVDatabase.getInstance()
globalDb = ClientKVDatabaseGlobal.getInstance()
```

## 插件系统 (architect.plugins)

提供热插拔插件机制：

```python
from architect.plugins import PluginBase, LoadPlugin, ReloadPlugins

class MyPlugin(PluginBase):
    def onLoad(self):
        print('Plugin loaded')

    def onUnload(self):
        print('Plugin unloaded')

# 加载插件
LoadPlugin(MyPlugin)

# 热重载
ReloadPlugins()
```

## 工具集合 (architect.tools)

```python
from architect.tools import *

# 代码生成工具
generate_md_html  # Markdown → HTML 转换
generate_lang     # 语言文件生成
```

## 不安全模块 (architect.core.unreliable)

```python
from architect.core.unreliable import Unreliable

# 提供 try-call 封装，防止单个异常影响整体流程
class MyClass(Unreliable):
    def risky_method(self):
        raise Exception('Error')

obj = MyClass()
obj.tryCall(obj.risky_method)  # 不会抛出异常