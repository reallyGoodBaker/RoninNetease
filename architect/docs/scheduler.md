# Scheduler — 调度系统

调度系统提供了多级任务调度机制：游戏 Tick 调度、渲染帧调度、固定频率调度和事件驱动调度。所有调度均通过装饰器声明，由框架自动管理注册和生命周期。

---

## 1. 架构

```
SchedulerManager (框架内部)
├── tickSched: Scheduler       ← Tick 调度器
│   ├── TIMER_TASK             定时/间隔任务
│   ├── BeforeUpdate           更新前
│   ├── Update                 更新中（默认）
│   └── AfterUpdate            更新后
│
├── renderSched: Scheduler     ← 渲染调度器（仅客户端）
│   ├── TIMER_TASK
│   ├── BeforeUpdate
│   ├── Update
│   └── AfterUpdate
│
└── fixedSchedulers: dict      ← 固定频率调度器（按子系统管理）
    ├── MyFixedSched: SimpleFixedScheduler(0.5)
    └── ...
```

---

## 2. `Scheduler` — 核心调度器

`Scheduler` 是一个基于队列的任务调度器，支持以下特性：

- **多阶段调度**：`BeforeUpdate → Update → AfterUpdate`
- **定时任务**：`TIMER_TASK` 队列独立于阶段调度
- **可暂停任务**：`SuspendableTask` 基于 Python 生成器
- **重入保护**：检测并跳过重入帧
- **任务移除**：按 ID 或按队列清空

### 2.1 核心方法

| 方法 | 说明 |
|---|---|
| `addTask(flag, fn) -> int` | 添加普通任务，返回任务 ID |
| `addSuspendableTask(flag, generator) -> int` | 添加可暂停任务（生成器），返回任务 ID |
| `removeTask(flag, taskId=-1)` | 移除任务（taskId=-1 清空整个队列） |
| `execute(flag, args=[])` | 执行指定阶段的所有任务 |
| `executeSequence(*args) -> (dt, skipped)` | 按顺序执行所有阶段，返回时间增量和跳过帧数 |
| `getSkippedUpdates() -> int` | 获取累计跳过的帧数 |

### 2.2 任务类型

```python
class Task:
    id: int
    fn: function           # 普通可调用对象
    finished: bool

class SuspendableTask(Task):
    fn: generator          # 生成器函数
    gen: generator         # 生成器实例
    callOnce()             # 单步推进，StopIteration 后完成
```

---

## 3. `@Sched` 装饰器

### 3.1 Tick 调度

```python
from architect.core import Sched, SchedUpdateFlags

class MySystem(ServerSubsystem):
    canTick = True

    @Sched.Tick()                          # 默认 Update 阶段
    def onUpdate(self):
        pass

    @Sched.Tick(SchedUpdateFlags.BeforeUpdate)
    def beforeUpdate(self):
        """在子系统的 onUpdate 之前执行"""
        pass

    @Sched.Tick(SchedUpdateFlags.AfterUpdate)
    def afterUpdate(self):
        """在子系统的 onUpdate 之后执行"""
        pass
```

**执行顺序**（每帧）：
```
子系统 onUpdate(dt) → BeforeUpdate 任务 → Update 任务 → AfterUpdate 任务
```

### 3.2 Render 调度（仅客户端）

```python
@Sched.Render()                          # 默认 Update 阶段
def onRender(self):
    pass

@Sched.Render(SchedUpdateFlags.BeforeUpdate)
def beforeRender(self):
    pass
```

Render 调度在 `GameRenderTickEvent` 触发时执行，独立于 Tick 调度。

### 3.3 Fixed 调度（固定频率）

```python
class MySystem(ServerSubsystem):
    @Sched.Fixed('my_fixed_sched')  # 声明固定调度器名称
    def onFixedUpdate(self):
        """每 0.5 秒执行一次"""
        print('Fixed tick!')

    def onReady(self):
        # 在 onReady 中启动调度器
        sched = self.scheduleFixed('my_fixed_sched', period=0.5)
        # sched 是 SimpleFixedScheduler 实例

    def onDestroy(self):
        self.stopFixed('my_fixed_sched')
```

`scheduleFixed(name, period)`：
- `name` — 调度器名称（与 `@Sched.Fixed` 声明的名称一致）
- `period` — 执行间隔（秒）
- **必须**在 `onReady()` 中调用，不能在 `onInit()` 中调用（引擎未初始化）

### 3.4 Event 调度（事件驱动）

```python
class MySystem(ServerSubsystem):
    @Sched.Event('EntityHurtEvent', isCustom=False)
    def onEntityHurtSched(self):
        """EntityHurtEvent 触发时执行"""
        # 注意：不接收事件参数！
        pass

    @Sched.Event('EntityHurtEvent', isCustom=False,
                  scheduleFlag=SchedEventFlags.AfterEvent)
    def afterEntityHurt(self):
        """EntityHurtEvent 触发后执行（AfterEvent 阶段）"""
        pass
```

关键点：
- `@Sched.Event` 的方法**不接收** `ChainedEvent` 参数
- 如果需要访问事件数据，通过 `EventReader` 组件

---

## 4. 可暂停任务 — `SuspendableTask`

基于 Python 生成器的可暂停任务，每次 `callOnce()` 推进一个 `yield` 步：

```python
from architect.core import Scheduler

sched = Scheduler()

def my_generator():
    print('Step 1')
    yield
    print('Step 2')
    yield
    print('Step 3 - done')

task_id = sched.addSuspendableTask('Update', my_generator)

# 每次 execute('Update') 执行一步
sched.execute('Update')  # 打印 Step 1
sched.execute('Update')  # 打印 Step 2
sched.execute('Update')  # 打印 Step 3 - done，任务完成
```

---

## 5. 定时任务

### 5.1 周期性任务

```python
from architect.core.scheduler import Scheduler

sched = Scheduler()

# 每 tick 执行
sched.run(fn)

# 周期性执行（每 ticks 帧）
sched.runInterval(fn, ticks=10)

# 超时执行（仅一次）
sched.runTimeout(fn, ticks=60)
```

### 5.2 `TimerAdapter` — 引擎定时器

```python
from architect.core.scheduler import TimerAdapter

def on_timer():
    print('Engine timer tick!')

timer = TimerAdapter(0.5, on_timer)  # 0.5 秒间隔
timer.start()
timer.cancel()
```

`TimerAdapter` 封装了引擎的 `AddRepeatedTimer` / `CancelTimer` API。

---

## 6. `SimpleFixedScheduler` — 简易固定调度器

```python
from architect.core.scheduler import SimpleFixedScheduler

sched = SimpleFixedScheduler(0.5)  # 0.5 秒间隔
sched.scheduler.addTask('Update', my_task)
sched.start()
sched.cancel()
```

- 继承自 `SchedulerPoller`
- 内部使用 `TimerAdapter` 定时调用 `scheduler.executeSequence()`

---

## 7. `Future` — 异步 Promise

```python
from architect.core.scheduler import Future

# 手动创建
def my_executor(resolve, reject):
    # 异步操作完成后调用 resolve 或 reject
    resolve('done')

future = Future(my_executor)
future.done(lambda result: print('Success:', result))
future.expected(lambda error: print('Failed:', error))
```

**状态：**
- `Future.PENDING` (0) — 等待中
- `Future.FULFILLED` (1) — 已完成
- `Future.REJECTED` (2) — 已拒绝

**静态工厂：**
```python
future, resolve, reject = Future.resolvers()
# 外部控制 resolve/reject
resolve('success')
```

---

## 8. `@Async` — 协程装饰器

将生成器函数转换为返回 `Future` 的异步函数：

```python
from architect.core.scheduler import Async, Future

def fetch_data():
    """模拟异步操作，返回 Future"""
    ft, res, rej = Future.resolvers()
    # ... 异步请求
    res({'hp': 100})
    return ft

@Async
def load_player_data():
    data = yield fetch_data()
    print('Received:', data)
    return data['hp']

# 调用
result = load_player_data()
result.done(lambda hp: print('HP:', hp))
```

`@Async` 内部驱动生成器执行，自动等待 `yield` 出的 `Future` 完成后再推进下一步。

---

## 9. 调度阶段常量

```python
class SchedUpdateFlags:
    BeforeUpdate = 'BeforeUpdate'
    AfterUpdate = 'AfterUpdate'
    Update = 'Update'

class SchedEventFlags:
    Event = 'Event'
    AfterEvent = 'AfterEvent'
```

---

## 10. 完整示例

```python
from architect.core import SubsystemServer, ServerSubsystem
from architect.core import Sched, SchedUpdateFlags, SchedEventFlags
from architect.core.scheduler import Future

class GameplayScheduler(ServerSubsystem):
    canTick = True

    # === Tick 调度 ===

    @Sched.Tick(SchedUpdateFlags.BeforeUpdate)
    def collect_input(self):
        """每帧最先执行：收集输入"""
        pass

    @Sched.Tick()
    def update_physics(self):
        """Update 阶段：物理模拟"""
        pass

    @Sched.Tick(SchedUpdateFlags.AfterUpdate)
    def sync_state(self):
        """最后执行：同步状态"""
        pass

    # === 固定频率 ===

    @Sched.Fixed('auto_save')
    def auto_save(self):
        """每 30 秒自动保存"""
        print('[Save] Auto saving...')

    def onReady(self):
        self.scheduleFixed('auto_save', period=30.0)

    # === 事件驱动 ===

    @Sched.Event('EntityHurtEvent')
    def onEntityHurt(self):
        """实体受伤时执行"""
        pass

    # === 异步 ===

    def load_remote_data(self, url):
        ft, res, rej = Future.resolvers()
        # 模拟网络请求
        res({'data': 'loaded'})
        return ft

    def onReady(self):
        fut = self.load_remote_data('config_url')
        fut.done(lambda data: print('Config loaded:', data))
```

---

## 下一步

- [事件系统 (event.md)](event.md) — 事件系统详解
- [UI 系统 (ui.md)](ui.md) — 响应式 UI
- [Profiler (profiler.md)](profiler.md) — 性能诊断