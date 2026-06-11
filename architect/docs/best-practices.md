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

# 不好：一个系统做所有事情
class GodSystem(ServerSubsystem):
    def handle_combat(self): ...
    def handle_inventory(self): ...
    def handle_ai(self): ...
```

**通过 `CommandBus` 解耦：** 让子系统通过命令总线通信，而非直接引用。

```python
# 好：通过 CommandBus
class QuestSystem(ServerSubsystem):
    def onReady(self):
        manager = SubsystemManager.getInstance()
        self._unreg = manager.bus.register('quest.complete', self.on_quest_done)

# 不好：直接引用其他子系统
class QuestSystem(ServerSubsystem):
    def onReady(self):
        self.reward_sys = SubsystemManager.getInstance().getSubsystem(RewardSystem)
```

**在 `onReady` 中初始化跨系统依赖：** `onInit` 只初始化自身，等所有系统创建完毕后再在 `onReady` 中建立连接。

```python
class MySystem(ServerSubsystem):
    def onInit(self):
        self.data = {}          # ✅ 初始化自身状态

    def onReady(self):
        self.other = OtherSystem.getInstance()  # ✅ 获取其他系统
        self.start_fixed()                      # ✅ 启动固定调度器
```

### ❌ 避免

- 在 `onInit` 中调用 `serveFixed()` — 此时引擎未初始化
- 在 `onInit` 中通过 `getSubsystem()` 获取其他系统
- 忘记设置 `canTick = True` 导致 `onUpdate` 不执行

---

## 2. 组件设计

### ✅ 推荐

**纯数据容器：** 组件只存储数据，不含业务逻辑。

```python
# 好
class Health(Component):
    hp = 100
    maxHp = 100

# 不好：组件里写逻辑
class Health(Component):
    hp = 100
    maxHp = 100

    def take_damage(self, amount):   # 逻辑应该放在 System 中
        self.hp -= amount
        if self.hp <= 0:
            self.on_death()
```

**细粒度组件：** 拆分大组件为多个小组件，便于查询和复用。

```python
# 好：细粒度
class Position(Component):
    x = 0.0; y = 0.0; z = 0.0

class Velocity(Component):
    vx = 0.0; vy = 0.0; vz = 0.0

class Health(Component):
    hp = 100; maxHp = 100

# 不好：大杂烩
class EntityData(Component):
    x = 0.0; y = 0.0; z = 0.0
    vx = 0.0; vy = 0.0; vz = 0.0
    hp = 100; maxHp = 100
    inventory = []
    effects = {}
```

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
class Inventory(Component):
    items = PersistKeys()   # 标记需要持久化的字段集
    slots = [''] * 36
```

### ❌ 避免

- 在组件中编写带副作用的逻辑
- 组件的类属性使用可变默认值（如 `items = []`）— 所有实例共享同一个列表
- 忘记在需要持久化的组件上使用 `PersistKeys()`

---

## 3. 查询模式

### ✅ 推荐

**使用 `@Query(attach_query=True)` 自动注入：**

```python
@Query(target='{Health}', required=['{CombatStats}'], attach_query=True)
def damage_tick(self, entityId, Health, CombatStats=None):
    Health.hp -= 1  # 直接使用组件实例
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
@Query(target='{Health}')
def check_low_hp(self, entityId):
    health = getComponent(entityId, Health)
    if health and health.hp < 20:
        self.heal(entityId)
```

### ❌ 避免

- 在 `@Query` 方法内遍历实体再调用 `getComponent()` — 这是反模式
- 对频繁变化的组件使用大范围的 `target` 查询 — 用 `required` 代替

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

**在需要时中断事件流：**

```python
@EventListener('EntityHurtEvent')
def onEntityHurt(self, event):
    if event.id == self.god_player:
        event.stop()           # 阻止后续监听器
        event.setEvent('damage', 0)  # 修改伤害为 0
```

**区分引擎事件与自定义事件：**

```python
@EventListener('ServerPostInitEvent')   # 引擎事件 → isCustomEvent=False
def onInit(self, event): ...

@CustomEvent('MyDataSyncEvent')          # 自定义事件 → isCustomEvent=True
def onSync(self, event): ...
```

### ❌ 避免

- 在事件处理中执行耗时操作 — 考虑用 `@Sched.Event` 延迟处理
- 忘记 `event.stop()` 后仍需返回值或清理状态
- 混淆 `event.prevent()`（取消默认）和 `event.stop()`（停止传递）

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

- 在 `onInit` 中调用 `serveFixed()` — 引擎未就绪
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

    with profiler.record('Combat.heal_loop'):
        self.heal_tick()
```

**周期性输出报告：**

```python
if self.ticks % 300 == 0:
    snap = profiler.flush()
    for key, stats in snap.items():
        if stats['avg_ms'] > 5.0:   # 只输出超过 5ms 的
            print('[WARN] %s: avg=%.2fms max=%.2fms' %
                  (key, stats['avg_ms'], stats['max_ms']))
```

**生产环境禁用：**

```python
profiler.disable()  # 发布时关闭
```

### ❌ 避免

- 每帧都 `flush()` — 开销大且输出过多
- 用过细的 key 导致统计数据过于分散
- 在 profiler 开启时记录快速路径（< 0.1ms）— 几乎没有诊断价值

---

## 7. 插件设计

### ✅ 推荐

**插件只做功能扩展，不承载核心业务逻辑：**

```python
# 好：插件提供基础设施
@Plugin(name='DatabasePlugin', ver=[1, 0, 0])
class DatabasePlugin(PluginBase):
    def onAttach(self, manager):
        manager.bus.register('db.save', self.save)
        manager.bus.register('db.load', self.load)

# 子系统使用插件提供的基础设施
class PlayerSystem(ServerSubsystem):
    def save_player(self):
        SubsystemManager.getInstance().bus.execute('db.save', 'player_1', data)
```

**声明正确的依赖：**

```python
@Plugin(
    name='MyCombatPlugin',
    deps={
        'RoninAnimationEx': '>=1.0.0',   # 需要动画插件
        'RoninInputEx': '>=1.0.0'        # 需要输入插件
    }
)
```

### ❌ 避免

- 插件之间循环依赖
- 在插件中直接实例化子系统 — 应通过 `registerSubsystem`
- 插件做太多事情 — 一个插件一个关注点

---

## 8. 常见陷阱

### 8.1 可变默认值

```python
# ❌ 错误：所有 Health 实例共享同一个 effects 列表
class Health(Component):
    effects = []

# ✅ 正确：定义类属性作为默认值
class Health(Component):
    hp = 100
    maxHp = 100
    # effects 在创建时设置
```

组件的类属性用作默认值。对于需要实例独立值的字段，在 `createComponent` 后初始化。

### 8.2 装饰器注册顺序

```python
# ❌ 先 @SubsystemServer 后定义类会报错
@SubsystemServer  # ← Manager 此时可能未创建
class MySystem(ServerSubsystem): ...

# ✅ 正常流程下没问题（modMain.py → createServer() → 导入模块 → 装饰器执行）
```

确保 `modMain.py` 中先调用 `createServer()` / `createClient()`，再让模块被导入。

### 8.3 组件注册时机

```python
# ❌ 在 Manager 未完成初始化时创建组件
createComponent(entity_id, Health)  # → 组件未注册到引擎

# ✅ 在 onReady 或 Tick 中创建
def onReady(self):
    createComponent(entity_id, Health)
```

---

## 9. 目录结构建议

```
your_mod/
├── modMain.py               # 入口
├── conf.py                  # 配置
├── subsystems/              # 子系统（按领域分）
│   ├── combat/
│   │   ├── __init__.py
│   │   ├── server.py       # 服务端战斗系统
│   │   └── client.py       # 客户端战斗系统
│   ├── inventory/
│   └── quest/
├── components/              # 组件（按数据域分）
│   ├── combat.py           # Health, CombatStats
│   ├── inventory.py        # Inventory
│   └── player.py           # PlayerStats
├── plugins/                 # 用户插件
│   └── my_plugin.py
├── events/                  # 自定义事件定义（可选）
│   └── custom_events.py
└── utils/                   # 工具函数
    └── helpers.py
```

---

## 10. Python 2.7 注意事项

- 使用 `# coding=utf-8` 声明文件编码
- `print` 是语句，不是函数（`print 'hello'`）
- `dict.items()` 返回 list，不是 view
- 字符串格式使用 `%` 或 `.format()`，没有 f-string
- 生成器返回值通过 `StopIteration` 异常传递
- 不要使用 `async` / `await` 关键字
- 类定义使用 `class Foo(object):` 显式继承 object

---

## 下一步

- [快速开始 (quickstart.md)](quickstart.md) — 返回入门教程
- [架构设计 (architecture.md)](architecture.md) — 理解设计决策
- [子系统 (subsystem.md)](subsystem.md) — 子系统 API 参考