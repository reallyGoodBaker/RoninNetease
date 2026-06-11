# Best Practices — 最佳实践

本文档汇总了使用 RoninNetease 框架时的推荐模式、设计决策和常见陷阱。

---

## 1. 子系统设计

### ✅ 推荐

**单一职责：** 每个子系统只负责一个领域。

```python
# 好：职责分离
class CombatSystem(ServerSubsystem):    # 战斗逻辑
    pass

class InventorySystem(ServerSubsystem): # 物品管理
    pass

class SpawnSystem(ServerSubsystem):     # 实体生成
    pass
```

**通过 `CommandBus` 解耦：** 让子系统通过命令总线通信，而非直接引用。

```python
# 好：通过 CommandBus
class QuestSystem(ServerSubsystem):
    def onReady(self):
        manager = SubsystemManager.getInstance()
        self._unreg = manager.bus.register('quest.complete', self.on_quest_done)
```

**在 `onReady` 中初始化跨系统依赖：** `onInit` 只初始化自身，等所有系统创建完毕后再在 `onReady` 中建立连接。

```python
class MySystem(ServerSubsystem):
    def onInit(self):
        self.data = {}          # ✅ 初始化自身状态

    def onReady(self):
        self.other = OtherSystem.getInstance()          # ✅ 获取其他系统
        self.scheduleFixed('my_fixed', period=1.0)     # ✅ 启动固定调度器
```

### ❌ 避免

- 在 `onInit` 中调用 `scheduleFixed()` — 此时引擎未初始化
- 在 `onInit` 中通过 `getSubsystem()` 获取其他系统
- 忘记设置 `canTick = True` 导致 `onUpdate` 不执行
- 使用不存在的 `getManager()` 方法 — 应使用 `SubsystemManager.getInstance()`

---

## 2. 组件设计

### ✅ 推荐

**纯数据容器：** 组件只存储数据，不含业务逻辑。

```python
class Health(Component):
    hp = 100
    maxHp = 100
```

**细粒度组件：** 拆分大组件为多个小组件，便于查询和复用。

**使用 `@DefineFields` 做验证：**

```python
@DefineFields({
    'level': FieldSchema(default=1, validator=lambda v: v >= 1),
    'xp': FieldSchema(default=0, validator=lambda v: v >= 0),
})
class PlayerStats(Component):
    pass
```

**标记持久化字段：**

```python
@PersistKeys('slots')
class Inventory(Component):
    slots = [''] * 36
```

### ❌ 避免

- 在组件中编写带副作用的逻辑
- 组件的类属性使用可变默认值（如 `items = []`）

---

## 3. 查询模式

### ✅ 推荐

`@Query` 接收组件类作为位置参数，用 `EntityId` 获取实体 ID：

```python
from architect.query import Query, EntityId

@Query(Health, EntityId, required=[CombatStats])
def damage_tick(self, health, entityId):
    # 注：required 中的 CombatStats 仅用于筛选，不注入到参数
    health.hp -= 1
```

**在 `onUpdate` 中调用查询方法：**

```python
class DamageSystem(ServerSubsystem):
    canTick = True

    def onUpdate(self, dt):
        self.damage_tick()  # 遍历所有匹配实体
```

**按需使用手动获取：**

```python
health = getComponent(entityId, Health)
if health and health.hp < 20:
    self.heal(entityId)
```

### ❌ 避免

- 在 `@Query` 方法内遍历实体再调用 `getComponent()`
- 误用不存在的 `target`/`attach_query` 参数 — `@Query` 只接受位置组件参数和 `required`/`excluded` 选项

---

## 4. 事件系统

### ✅ 推荐

**使用 `@EventListener` 装饰器：**

```python
@EventListener('EntityHurtEvent')
def onEntityHurt(self, event):
    entityId = event.id        # ✅ 使用属性访问
    damage = event.damage
```

**区分引擎事件与自定义事件：**

```python
@EventListener('ServerPostInitEvent')   # 引擎事件
def onInit(self, event): ...

@CustomEvent('MyDataSyncEvent')          # 自定义事件
def onSync(self, event): ...
```

---

## 5. 调度系统

### ✅ 推荐

**利用多阶段调度：**

```python
@Sched.Tick(SchedUpdateFlags.BeforeUpdate)  # 输入收集
def collect_input(self): ...

@Sched.Tick()                                # 逻辑更新
def update_logic(self): ...

@Sched.Tick(SchedUpdateFlags.AfterUpdate)    # 状态同步
def sync_state(self): ...
```

**固定调度器在 `onReady` 中启动：**

```python
@Sched.Fixed('save_scheduler')
def auto_save(self): ...

def onReady(self):
    self.scheduleFixed('save_scheduler', period=30.0)  # ✅ 在 onReady
```

### ❌ 避免

- 在 `onInit` 中调用 `scheduleFixed()` — 引擎未就绪
- 在 `@Sched.Event` 中尝试访问事件参数 — 应使用 `EventReader` 组件
- 创建过多固定频率调度器 — 合并到少数调度器中

---

## 6. 性能诊断

### ✅ 推荐

**关键路径计时：**

```python
def onUpdate(self, dt):
    with profiler.record('Combat.damage_loop'):
        self.damage_tick()
```

**周期性输出报告：**

```python
if self.ticks % 300 == 0:
    snap = profiler.flush()
    for key, stats in snap.items():
        if stats['avgMs'] > 5.0:   # 只输出超过 5ms 的
            print('[WARN] %s: avg=%.2fms max=%.2fms' %
                  (key, stats['avgMs'], stats['maxMs']))
```

---

## 7. UI 系统

### ✅ 推荐

`signal()` 不是装饰器，返回 `(getter, setter)` 元组：

```python
from architect.ui.client import signal, Sink

class MyHUD(UiSubsystem):
    def onCreate(self):
        self.hpGet, self.hpSet = signal(100)

    @Sink  # 无参数
    def refresh(self):
        hp = self.hpGet()
        self.find('/hpLabel').SetText(str(hp))
```

`@UiDef`、`@Screen`、`@Hud`、`@AutoCreate` 都是**类装饰器**：

```python
@UiDef('myHud')
@Screen
@AutoCreate
class MyHUD(UiSubsystem):
    pass
```

### ❌ 避免

- 把 `signal()` 当装饰器使用
- 给 `@Sink` 传 `initiator` 参数
- 把 `@UiDef`/`@Screen` 用在方法上

---

## 8. 远程调用 (RPC)

### ✅ 推荐

使用 `remote.client` 和 `remote.server` 单例：

```python
from architect.remote.common import remote

# 客户端调用服务端（fire-and-forget）
remote.client.call('MySystem.method', arg1, arg2)

# 客户端调用服务端（需要返回值）
fut = remote.client.invoke('MySystem.method', arg1, arg2)
fut.done(lambda result: print(result))

# 服务端调用客户端
remote.server.call(playerId, 'ClientSystem.method', arg1)
remote.server.callEvery('ClientSystem.method', arg1)  # 广播

# 注册可远程调用的方法
class MySystem(ServerSubsystem):
    @Remote
    def my_method(self, caller_playerId, *args, **kwargs):
        pass
```

### ❌ 避免

- 使用不存在的 `callRemote()` 函数

---

## 9. 常见陷阱

### 9.1 可变默认值

```python
class Health(Component):
    hp = 100         # ✅ 不可变默认值 OK
    maxHp = 100
```

组件的类属性用作默认值。对于需要实例独立值的字段，在 `createComponent` 后初始化。

### 9.2 API 名称错误

| ❌ 错误 | ✅ 正确 |
|---|---|
| `self.getManager()` | `SubsystemManager.getInstance()` |
| `callRemote(...)` | `remote.client.invoke(...)` 或 `remote.client.call(...)` |
| `@signal` (装饰器) | `signal(default)` 函数调用，返回 `(get, set)` |
| `@Sink(initiator=hp)` | `@Sink` (无参数) |
| `@Query(target='{Health}')` | `@Query(Health, EntityId)` |
| `serveFixed('name')` | `self.scheduleFixed('name', period=1.0)` |
| `Sched.Tick.BeforeUpdate` | `SchedUpdateFlags.BeforeUpdate` |
| `@UiDef('name')` 在方法上 | `@UiDef('name')` 在**类**上 |

### 9.3 装饰器注册顺序

确保 `modMain.py` 中先调用 `createServer()` / `createClient()`，再让模块被导入。

---

## 10. 目录结构建议

```
your_mod/
├── modMain.py               # 入口
├── conf.py                  # 配置
├── subsystems/              # 子系统
├── components/              # 组件
├── plugins/                 # 用户插件
└── utils/                   # 工具函数
```

---

## 11. Python 2.7 注意事项

- 使用 `# coding=utf-8` 声明文件编码
- `print` 是语句，不是函数（`print 'hello'`）
- `dict.items()` 返回 list，不是 view
- 字符串格式使用 `%` 或 `.format()`，没有 f-string
- 生成器返回值通过 `StopIteration` 异常传递
- 类定义使用 `class Foo(object):` 显式继承 object

---

## 下一步

- [快速开始 (quickstart.md)](quickstart.md) — 返回入门教程
- [架构设计 (architecture.md)](architecture.md) — 理解设计决策
- [子系统 (subsystem.md)](subsystem.md) — 子系统 API 参考