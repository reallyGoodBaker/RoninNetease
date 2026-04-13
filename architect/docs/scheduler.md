# 调度系统 (Scheduler)

调度系统提供了灵活的任务执行机制，支持 tick、渲染帧以及固定频率的任务调度。

## @Sched 装饰器

在子系统内部，可以使用 `@Sched` 装饰器定义定时任务。

### @Sched.Tick()
每一 tick 执行一次。
```python
@Sched.Tick()
def onTick(self):
    # 逻辑代码
    pass
```

### @Sched.Render()
每一渲染帧执行一次（仅限客户端子系统）。
```python
@Sched.Render()
def onRender(self):
    # 适合处理 UI 平滑过渡或特效
    pass
```

### @Sched.Fixed(name)
按固定频率执行。需要先通过 `scheduleFixed` 启动调度器。
```python
@SubsystemServer
class MyService(ServerSubsystem):
    def onReady(self):
        # 启动一个名为 'sec1' 的调度器，周期为 1.0 秒
        self.scheduleFixed('sec1', 1.0)

    @Sched.Fixed('sec1')
    def onTimer(self):
        print("执行定时任务")
```

### @Sched.Event(eventType, isCustom=False)
当特定事件触发时，作为调度任务执行。

## 任务顺序 (Flags)
调度任务可以指定在 tick 的不同阶段执行：
- `BeforeUpdate`: 在标准 update 之前。
- `Update`: (默认) 标准 update 阶段。
- `AfterUpdate`: 在标准 update 之后。

```python
from ..architect.conf import SchedUpdateFlags

@Sched.Tick(SchedUpdateFlags.AfterUpdate)
def lateUpdate(self):
    pass
```

## 编程式任务 (Scheduler API)

除了装饰器，你也可以通过子系统获取调度器实例来手动管理任务：

- `run(fn)`: 立即在下一帧/tick 执行。
- `runTimeout(fn, ticks)`: 延迟指定 tick 数后执行一次。
- `runInterval(fn, ticks)`: 每隔指定 tick 数循环执行。
- `clearTimeout(taskId)`: 取消已排期的任务。

```python
def onInit(self):
    # 在客户端 tick 调度器中运行一个定时任务
    from ..subsystem import SubsystemManager
    SubsystemManager.clientTickSched.runInterval(self.my_task, 20)
```

## 协程支持 (SuspendableTask)
调度器内部支持生成器形式的协程任务，通过 `addSuspendableTask` 手动添加。
```python
def my_coroutine(self):
    print("Step 1")
    yield
    print("Step 2")

# 在 Scheduler 实例中添加
# manager.clientTickSched.addSuspendableTask(SchedUpdateFlags.Update, self.my_coroutine)
```
> 注意：通常建议优先使用标准的装饰器。
