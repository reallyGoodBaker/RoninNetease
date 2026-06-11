# RoninNetease 架构设计

## 为什么存在这个框架

网易基岩版《我的世界》模组 SDK（`mod.client.extraClientApi` / `mod.server.extraServerApi`）提供了一个底层的事件驱动的 API，但没有提供任何业务逻辑组织方式。

典型原始开发的代码结构：

```python
# 所有逻辑平铺在 listen/import 回调中
def on_tick():
    for entityId in global_entity_list:
        comp = api.CreateComponent(entityId, 'xxx', 'Health')
        if comp and comp.value <= 0:
            api.DestroyEntity(entityId)
```

随着模组规模增长（实体类型增多、子系统间依赖复杂），这种模式迅速退化为**面条式代码**——状态散落在全局字典中、生命周期失控、实体遍历每次都全量扫描 O(n)、子系统间硬引用耦合。

RoninNetease 的目标是将这些痛点一一解决，同时保持 Python 2 兼容性。

## 分层设计

```
┌──────────────────────────────────────────────────────────┐
│                 compact.py  (统一入口)                     │
├──────────────────────────────────────────────────────────┤
│  UI Layer      │  FSM       │  Remote (RPC)               │
│  Signal/Sink   │  StateTree │  DataTable serialization    │
├──────────────────────────────────────────────────────────┤
│  Query Layer   │  Event Layer                             │
│  @Query        │  EventChain / EventSignal / EventTarget │
│  CompIndex     │  @EventListener / ChainedEvent           │
├──────────────────────────────────────────────────────────┤
│  Component Layer │  Scheduler Layer                       │
│  CRUD / Marker   │  Tick / Render / Fixed / Event        │
│  Schema / Persist│  Future / Async                        │
├──────────────────────────────────────────────────────────┤
│  SubsystemManager  │  Plugin Loader  │  CommandBus         │
│  Lifecycle / Tick  │  Dep Topology   │  Subsystem decouple │
├──────────────────────────────────────────────────────────┤
│  Annotation System │  Profiler  │  Config (HOT_RELOADABLE) │
├──────────────────────────────────────────────────────────┤
│  NetEase SDK (mod.client.extraClientApi / mod.server)     │
└──────────────────────────────────────────────────────────┘
```

## 核心设计决策

### 1. 装饰器驱动 vs 显式注册

**选择**：装饰器驱动。

```python
# 框架方式
@Sched.Tick()
@Query(EntityId, HealthComponent)
def handle(self, entityId, health):
    ...

# 对比显式注册方式
manager.tickScheduler.register('update', lambda dt: handle(dt))
manager.queryEngine.register(HealthComponent, handle)
```

**原因**：
- 网易模组开发者的主力 IDE（PyCharm + MC Dev Kit）对装饰器的代码补全和跳转支持良好
- 声明式代码在阅读时比注册式代码更容易理解「这个方法在何时被调用」
- `@Query` 的参数在装饰时就能做静态检查（组件是否存在）

**代价**：隐式行为增多，调用栈中包含多层 wrapper，调试时需理解注解系统的工作原理。

### 2. CompIndex 反向索引 vs Archetype

**选择**：组件名 → 实体 ID 集合的反向索引，Query 时求交集。

**原因**：
- 网易 SDK 的组件存储在 C++ 引擎侧，框架只能通过字符串名称创建/销毁组件，无法在 Python 侧控制组件的内存布局（Archetype 的前提不成立）
- 集合交集 O(min(m,n)) 的性能在实际模组中（通常实体持有 5-15 个组件）远优于全量遍历 O(n)
- 按集合大小升序排列后逐级裁剪，充分利用了「稀有组件」的过滤效果

### 3. SubsystemManager + subsystem 双接口

**选择**：`SubsystemManager`（实例）负责生命周期管理，`subsystem`（静态类）提供快捷访问。

**原因**：
- 大部分模组只有一个主导子系统（Server 端一个，Client 端一个），`subsystem.sendServer()` 比 `SubsystemManager.getInstance().getSubsystem(MySystem).sendServer()` 简洁得多
- 当需要多子系统协作时，`SubsystemManager.getSubsystem()` 提供精确控制
- `subsystem` 类代理第一个注册的子系统，这是一个「80% 场景的便捷层」

### 4. 调度器重入保护

**选择**：跳过而非排队。

```python
if self._sequenceExecuting:
    self._skippedUpdates += 1
    return  # 直接跳过
```

**原因**：
- 网易 SDK 的 Tick 回调是单线程同步调用，不存在真正并发的重入
- 跳过而非排队的理由是：如果上一次 `executeSequence` 还未完成，说明某任务耗时超过了一个 Tick 周期。此时排队会导致任务堆积并延迟越来越大，跳过反而是止损
- 跳过的帧数通过 `getSkippedUpdates()` 暴露给 Profiler，开发者可以从诊断快照中感知到性能瓶颈

### 5. Python 2 兼容性策略

**选择**：`# type:` 注释 + `if 1 > 2` hack。

**原因**：
- Python 2 没有 PEP 484 类型注解语法
- `# type:` 是 PyCharm/VS Code 等 IDE 支持的非标准类型标注方式
- `if 1 > 2: return cls()` 利用死代码分支让类型检查器推断返回值类型为 `cls`，否则返回 `None` 会导致所有调用处报类型警告
- 这些代码在有类型注解的 Python 3 中是冗余的，但在 Py2 + IDE 类型检查的组合中是不可或缺的

## 数据流

```
游戏引擎 Tick / Render 事件
        │
        ▼
  SubsystemManager.tickSubsystem()
        │
        ├─► 遍历 subsystems, 调用 onUpdate(dt)
        │       │
        │       └─► Profiler.record('XxxSystem.onUpdate')
        │
        └─► tickSched.executeSequence()
                │
                ├─► TimerTask 队列
                ├─► BeforeUpdate 队列
                ├─► Update 队列       ← @Sched.Tick() 方法在此执行
                │       │
                │       └─► @Query 装饰器
                │               │
                │               └─► CompIndex.queryEntities()
                │                       │
                │                       └─► 集合交集 → 候选 entityId 列表
                │                               │
                │                               └─► getComponentWithQuery()
                │                                       │
                │                                       └─► 检查 required/excluded
                │                                               │
                │                                               └─► 注入参数, 调用 fn()
                │
                └─► AfterUpdate 队列

Profiler.flush() → {
    'HealthSystem.onUpdate': {'avg_ms': 1.2, 'max_ms': 3.4, 'count': 60},
    'scheduler.tickSkipped': {'avg_ms': 0.0, 'max_ms': 0.0, 'count': 60},
}
```

## 模块职责矩阵

| 模块 | 职责 | 依赖 |
|------|------|------|
| `core/subsystem.py` | 生命周期管理、Tick 驱动 | event, scheduler, component, remote |
| `core/scheduler.py` | 四类调度执行 | basic, conf |
| `core/loader.py` | 插件发现/依赖排序/加载 | subsystem, configurator |
| `core/bus.py` | 子系统间同步通信 | 无 |
| `core/profiler.py` | 性能诊断 | 无 |
| `core/configurator.py` | 配置读取 + 热更新 | basic |
| `component/core.py` | ECS CRUD + CompIndex | annotation, event, schema |
| `component/schema.py` | 组件字段声明与验证 | 无 |
| `query/common.py` | @Query 注入 + CompIndex 查询 | component |
| `event/core.py` | EventSignal, EventChain, ChainedEvent | unreliable |
| `remote/common.py` | 跨端 RPC + Future | scheduler, subsystem |
| `ui/client.py` | 响应式 UI (Signal/Sink) | event, subsystem |