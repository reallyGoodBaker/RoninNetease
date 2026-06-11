# Molang — 表达式工具

Molang 是 Minecraft 内置的表达式语言。RoninNetease 提供了类型安全的读写封装，支持**命名变量**、**Query 变量**和**实体变量**的增删改查。

---

## 1. 概述

```
architect.utils.molang
├── types.py     ← 抽象基类（MolangReadable, MolangMutable 等）
├── common.py    ← NamedVariable, NamedEntityVariable
├── client.py    ← QueryVariable, ReactiveQueryVariable, @MolangQuery, MolangClient
└── server.py    ← NamedProperty, MolangServer
```

---

## 2. 抽象类型 — `types.py`

定义了 Molang 读写操作的接口：

| 基类 | 方法 |
|---|---|
| `MolangReadable` | `getValue(self, actorId, defaultValue)` |
| `MolangMutable(MolangReadable)` | `setValue(self, actorId, value)` |
| `EntityMolangReadable` | `getValue(self, defaultValue)` |
| `EntityMolangMutable(EntityMolangReadable)` | `setValue(self, value)` |

---

## 3. 命名变量 — `common.py`

### 3.1 `NamedVariable` — 实体变量（`v.{name}`）

```python
from architect.utils.molang.common import NamedVariable

# 创建变量
myVar = NamedVariable('speed')     # 自动加前缀 → 'v.speed'

# 读取
val = myVar.getValue(actorId, defaultValue=0)

# 写入（自动执行 Molang 赋值表达式）
myVar.setValue(actorId, 1.5)       # 等效 v.speed = 1.5

# 获取完整 Molang 名称
print(myVar.getMolangName())       # 'v.speed'
```

### 3.2 `NamedEntityVariable` — 无 actor 参数的实体变量

```python
from architect.utils.molang.common import NamedEntityVariable

# 构造函数直接绑定实体和变量名
var = NamedEntityVariable(entityId, 'speed', defaultValue=0)

# 读写无需传 actorId
val = var.getValue()
var.setValue(2.0)

# 获取 Molang 名称
print(var.getName())   # 'v.speed'
```

---

## 4. 客户端 Query 变量 — `client.py`

### 4.1 `QueryVariable` — query.mod 变量

```python
from architect.utils.molang.client import QueryVariable

# 创建并注册 query.mod 变量
qv = QueryVariable('playerLevel', defaultValue=0)
# 自动注册为 'query.mod.playerLevel'

# 读写
val = qv.getValue(actorId)
qv.setValue(actorId, 10)

# 监听值变化
qv.OnValueChanged.on(lambda actorId, value: print('Changed:', actorId, value))
```

### 4.2 `ReactiveQueryVariable` — 自动计算变量

```python
from architect.utils.molang.client import ReactiveQueryVariable

# 定义计算函数（返回计算值）
def calcLevel(actorId):
    return getComponent(actorId, PlayerStats).level

# 创建响应式变量
rqv = ReactiveQueryVariable('playerLevel', calc=calcLevel)
rqv.update(actorId)  # 手动触发一次更新
```

### 4.3 `@MolangQuery` — Query 变量装饰器

```python
from architect.utils.molang.client import MolangQuery

@MolangQuery
def playerHealth(actorId):
    """普通 query 变量，只在本地使用"""
    return getComponent(actorId, Health).hp

@MolangQuery(shared=True)
def playerLevel(actorId):
    """共享变量：变化时广播到其他客户端"""
    return getComponent(actorId, PlayerStats).level
```

被 `@MolangQuery` 装饰的函数作为 `ReactiveQueryVariable` 的计算函数。`shared=True` 时会通过 `MolangClient.broadcastQuery()` 发送到服务端再广播给其他客户端。

### 4.4 `MolangClient` 子系统

```python
from architect.utils.molang.client import MolangClient

# 服务端会自动注册 @SubsystemClient MolangClient
# 它在 onRender 中自动更新所有 ReactiveQueryVariable
# 并监听 'ronin_molang_query' 自定义事件同步共享变量
```

---

## 5. 服务端 — `server.py`

### 5.1 `NamedProperty` — 实体属性

```python
from architect.utils.molang.server import NamedProperty

prop = NamedProperty('strength')   # 通过 v.property('strength') 操作

# 读取（使用 EvalMolangExpression）
val = prop.getValue(actorId)       # 可能返回 None（出错时）

# 写入（使用 SetPropertyValue）
prop.setValue(actorId, 100)
```

### 5.2 `MolangServer` 子系统

```python
from architect.utils.molang.server import MolangServer

# 自动注册，处理以下功能：
# - 监听 'ronin_molang_query' 事件 → 广播到所有客户端
# - sendQuery(id, name, value) → 向所有客户端发送查询
```

---

## 6. 完整示例

```python
# 客户端：将组件值暴露为 Molang 变量
from architect.utils.molang.client import QueryVariable, MolangQuery
from architect.utils.molang.common import NamedVariable

@MolangQuery
def playerHealth(actorId):
    """本地 query 变量，每渲染帧自动同步"""
    health = getComponent(actorId, Health)
    return health.hp if health else 0

# 创建 v.score 实体变量
score = NamedVariable('score')
score.setValue(actorId, 1000)
print(score.getValue(actorId))  # 1000

# 在 Molang JSON 中使用：v.score、query.mod.playerHealth
```

---

## 下一步

- [数学库 (math.md)](math.md) — 向量和矩阵
- [组件系统 (ecs.md)](ecs.md) — 组件操作