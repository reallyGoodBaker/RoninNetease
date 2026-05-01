# 调度器系统

`architect` 的调度器系统为子系统提供声明式的调度方法注册，同时提供了独立的任务调度、异步编程和定时器能力。

## 概述

调度器是一个基于 Tick 循环的任务执行框架，每一帧按顺序执行各个阶段的任务。

### Scheduler 核心方法

```python
from architect.core.scheduler import Scheduler

sched = Scheduler()

# 添加任务到指定阶段
task_id = sched.addTask('Update', my_fn)

# 指定阶段执行
sched.execute('Update')

# 执行完整序列（TimerTask -> BeforeUpdate -> Update -> AfterUpdate）
sched.executeSequence()

# 添加可挂起任务（生成器函数）
sched.addSuspendableTask('Update', my_generator)

# 移除任务
sched.removeTask('Update', task_id)

# 移除某个阶段的所有任务
sched.removeTask('Update')
```

## 调度阶段

调度器按固定序列执行任务，顺序为：

1. **`TimerTask`** - 定时任务（通过 `addPeriodicTask`、`runTimeout`、`runInterval` 注册）
2. **`BeforeUpdate`** - 更新前
3. **`Update`** - 正常更新
4. **`AfterUpdate`** - 更新后

## 便捷定时器方法

```python
sched = Scheduler()

# 延迟执行（指定 tick 数后执行一次）
sched.runTimeout(my_fn, ticks=20)

# 间隔执行（每隔指定 tick 数执行一次）
sched.runInterval(my_fn, ticks=10)

# 下次 tick 执行
sched.run(my_fn)

# 取消定时任务
sched.clearTimeout(task_id)
```

## 装饰器风格的调度注册

通过 `@Sched` 装饰器可以在 Subsystem 中声明式地注册调度方法：

```python
from architect.core.scheduler import Sched

class MySystem(ServerSubsystem):

    @Sched.Tick()  # 默认为 Update 阶段
    def on_tick(self):
        pass

    @Sched.Tick(scheduleFlag=SchedUpdateFlags.BeforeUpdate)
    def before_update(self):
        pass

    @Sched.Tick(scheduleFlag=SchedUpdateFlags.AfterUpdate)
    def after_update(self):
        pass

    @Sched.Render()  # 仅在客户端生效
    def on_render(self):
        pass

    @Sched.Fixed('my_sched')  # 固定频率调度器
    def on_fixed(self):
        pass

    @Sched.Event('PlayerJoinEvent')  # 事件时调度
    def on_player_join(self):
        pass
```

### 调度类型

- **`@Sched.Tick()`** - 每帧执行, 跟随主 Tick 循环
- **`@Sched.Render()`** - 每渲染帧执行（仅客户端）
- **`@Sched.Fixed(schedulerName)`** - 固定频率执行，需调用 `scheduleFixed` 启动
- **`@Sched.Event(eventType)`** - 事件触发时执行（与 `EventReader` 配合）

## 游戏引擎定时器

直接使用游戏引擎的定时器 API：

```python
from architect.core.scheduler import addTimer, cancelTimer

# 添加周期定时器（秒）
timer = addTimer(1.0, my_fn)

# 取消定时器
cancelTimer(timer)
```

## TimerAdapter

`TimerAdapter` 是游戏引擎定时器的简单封装：

```python
from architect.core.scheduler import TimerAdapter

timer = TimerAdapter(1.0, my_fn)
timer.start()
timer.cancel()
```

## 固定频率调度器 `SimpleFixedScheduler`

`SimpleFixedScheduler` 是一个完整的周期性调度器，自带内部 `Scheduler`：

```python
from architect.core.scheduler import SimpleFixedScheduler

sched = SimpleFixedScheduler(period=1.0)

# 添加任务
sched.scheduler.addTask('Update', my_fn)

# 启动
sched.start()

# 停止
sched.cancel()
```

## 可挂起任务 `SuspendableTask`

`SuspendableTask` 支持生成器函数，每次 tick 执行一步：

```python
def my_generator():
    yield  # 暂停
    print("step 1")
    yield  # 暂停
    print("step 2")

sched.addSuspendableTask('Update', my_generator)
```

## 异步编程 `Future` 和 `@Async`

`Future` 和 `@Async` 装饰器提供了基于生成器的协程支持：

```python
from architect.core.scheduler import Future, Async

# 创建 Future
def executor(resolve, reject):
    resolve(42)

ftr = Future(executor)

# 注册回调
ftr.done(lambda v: print("Result:", v))
ftr.expected(lambda e: print("Error:", e))

# 异步协程
@Async
def my_coro():
    result = yield some_future()
    print("Got:", result)
    return result * 2

# 调用异步函数
my_coro().done(lambda v: print("Final:", v))