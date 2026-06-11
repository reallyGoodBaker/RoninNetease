# Utils — 工具集

RoninNetease 提供多个工具模块，涵盖设备信息、Molang 表达式、Persona 渲染覆盖、绘图和增强函数。

---

## 1. 概述

```
architect.utils
├── device/       ← 设备信息（客户端/服务端）
│   ├── client.py
│   └── server.py
├── molang/       ← Molang 表达式工具
│   ├── client.py
│   ├── server.py
│   ├── common.py
│   └── types.py
├── persona/      ← Persona 渲染覆盖
│   ├── client.py
│   └── server.py
├── enhance/      ← 增强函数与列表
│   ├── fn.py
│   └── list.py
├── drawing.py    ← 粒子绘图
├── client.py     ← 客户端工具
├── server.py     ← 服务端工具
└── export.py     ← 导出清单
```

---

## 2. 设备信息 — `device/`

### 2.1 客户端

```python
from architect.utils.device.client import DeviceClient

# 获取设备信息
info = DeviceClient.get_device_info()
# 返回包含设备型号、操作系统等的字典
```

### 2.2 服务端

```python
from architect.utils.device.server import DeviceServer
```

---

## 3. Molang 表达式 — `molang/`

Molang 是 Minecraft 内置的表达式语言，用于动画、渲染和粒子效果。

### 3.1 类型

```python
from architect.utils.molang.types import (
    MolangNumber,
    MolangString,
    MolangVariable,
    MolangExpression
)

# Molang 数值
val = MolangNumber('query.health / query.max_health')

# Molang 变量
var = MolangVariable('variable.is_running')
```

### 3.2 客户端

```python
from architect.utils.molang.client import MolangClient

# 设置 Molang 变量
MolangClient.set_variable(entity_id, 'variable.speed', 1.5)

# 获取 Molang 变量
value = MolangClient.get_variable(entity_id, 'variable.speed')
```

### 3.3 服务端

```python
from architect.utils.molang.server import MolangServer

# 服务端 Molang 操作
```

### 3.4 通用工具

```python
from architect.utils.molang.common import (
    molang_lerp,
    molang_clamp,
    molang_if_else
)

# Molang 条件表达式
expr = molang_if_else(
    'query.is_sprinting',
    '1.5',      # 冲刺时速度
    '1.0'       # 默认速度
)

# Molang 插值
blend = molang_lerp('0.0', '1.0', 'variable.blend_factor')
```

---

## 4. Persona 渲染覆盖 — `persona/`

Persona 系统允许修改玩家的渲染外观（皮肤、模型覆盖）。

### 4.1 客户端

```python
from architect.utils.persona.client import PersonaRendererComponent, PersonaEventsSubsystem

class MyPersonaSystem(ClientSubsystem):
    def onInit(self):
        # 获取 Persona 渲染组件
        self.renderer = PersonaRendererComponent.get()

    def change_skin(self, player_id):
        # 覆盖玩家渲染
        self.renderer.override_skin(player_id, 'custom:textures/skin.png')
        self.renderer.override_model(player_id, 'custom:models/armor.geo')

    def reset_skin(self, player_id):
        # 重置为默认
        self.renderer.reset(player_id)
```

### 4.2 服务端

```python
from architect.utils.persona.server import PersonaServer

class MyPersonaServer(ServerSubsystem):
    def onInit(self):
        self.persona = PersonaServer()

    def sync_skin_to_client(self, player_id, skin_path):
        # 通知客户端切换皮肤
        self.sendClient(player_id, 'OnPersonaChange', {
            'skin': skin_path
        })
```

---

## 5. 增强函数 — `enhance/`

### 5.1 `fn.py`

```python
from architect.utils.enhance.fn import (
    compVer,      # 版本号比较
    deep_merge,   # 深度合并字典
    safe_get      # 安全的嵌套访问
)

# 版本比较
# compVer([1, 1, 0], [1, 0, 0]) > 0  → True
result = compVer([1, 1, 0], [1, 0, 0])
if result > 0:
    print('Newer version')

# 深度合并
base = {'a': {'b': 1}}
override = {'a': {'c': 2}}
merged = deep_merge(base, override)
# → {'a': {'b': 1, 'c': 2}}

# 安全访问
value = safe_get(deep_dict, 'a.b.c', default=None)
```

### 5.2 `list.py`

```python
from architect.utils.enhance.list import (
    chunked,       # 列表分块
    flatten,       # 展平嵌套列表
    unique,        # 去重
    group_by       # 按 key 分组
)

# 分块
for batch in chunked(range(100), 10):
    process(batch)  # [0..9], [10..19], ...

# 展平
flat = flatten([[1, 2], [3, 4], [5]])
# → [1, 2, 3, 4, 5]

# 去重
uniq = unique([1, 2, 2, 3, 1])
# → [1, 2, 3]

# 分组
data = [{'type': 'A', 'val': 1}, {'type': 'B', 'val': 2}, {'type': 'A', 'val': 3}]
grouped = group_by(data, lambda x: x['type'])
# → {'A': [{'type':'A','val':1}, {'type':'A','val':3}], 'B': [{'type':'B','val':2}]}
```

---

## 6. 绘图 — `drawing.py`

```python
from architect.utils.drawing import Drawing

# 在客户端世界绘制
drawing = Drawing()

# 绘制粒子圆圈
drawing.circle(pos=Vec3(0, 64, 0), radius=5, color=(1, 0, 0), duration=1.0)

# 绘制线段
drawing.line(start=Vec3(0, 64, 0), end=Vec3(10, 64, 0), color=(0, 1, 0))

# 绘制矩形
drawing.rect(center=Vec3(0, 64, 0), size=(2, 3), color=(0, 0, 1))
```

`Drawing` 利用客户端粒子效果在世界上绘制临时图形，常用于调试和技能特效。

---

## 7. 客户端/服务端工具

### 7.1 客户端

```python
from architect.utils.client import ClientUtils

# 客户端专用工具函数
```

### 7.2 服务端

```python
from architect.utils.server import ServerUtils

# 服务端专用工具函数
```

---

## 8. 工具集导出清单

`architect/utils/export.py` 统一导出所有工具模块：

```python
from architect.utils.export import *

# 导出内容：
# - DeviceClient, DeviceServer
# - MolangClient, MolangServer
# - Drawing
# - 所有 enhance 函数
# - ClientUtils, ServerUtils
```

---

## 9. 编辑器工具 — `editor/tools/`

框架提供了开发阶段使用的 Node.js 工具（TypeScript 编写）：

### 9.1 `initProject.ts`

```bash
npx ts-node editor/tools/initProject.ts --name MyMod
```

功能：
- 生成 `modMain.py` 模板
- 生成 `conf.py` 配置模板
- 从 `manifest.json` 读取项目信息
- 创建推荐的目录结构（`subsystems/`、`components/`、`plugins/`）

### 9.2 `animExtractor.ts`

```bash
npx ts-node editor/tools/animExtractor.ts --input resources/animations/
```

功能：
- 从动画 JSON 文件中提取动画元数据
- 生成可用于 `$vendor.animation` 插件的动画配置

### 9.3 `utils.ts`

共享工具函数，处理文件路径、JSON 读写等。

---

## 下一步

- [数学库 (math.md)](math.md) — 向量和矩阵
- [FSM (fsm.md)](fsm.md) — 状态机
- [最佳实践 (best-practices.md)](best-practices.md) — 开发建议