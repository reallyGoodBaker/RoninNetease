# 调度系统

## 四种调度类型

| 装饰器 | 触发时机 | 运行环境 | 典型场景 |
|--------|----------|----------|----------|
| `@Sched.Tick()` | 每游戏 Tick (~50ms) | Server & Client | 游戏逻辑、AI |
| `@Sched.Render()` | 每渲染帧 | **仅 Client** | 特效、动画 |
| `@Sched.Fixed('name')` | 固定间隔（秒） | 任意 | 自动保存、心跳 |
| `@Sched.Event('EventName')` | 指定事件触发 | 任意 | 事件驱动任务 |

---

## 使用方式

```python
from architect.compact import Sched, SchedUpdateFlags, SchedEventFlags

class GameSystem(ServerSubsystem):

    @Sched.Tick(SchedUpdateFlags.Update)
    def every_tick(self, args):
        pass  # 每个 Tick 在 Update 阶段执行

    @Sched.Tick(SchedUpdateFlags.BeforeUpdate)
    def before_update(self, args):
        pass  # 在 Update 之前执行

    @Sched.Render()
    def every_frame(self, args):
        pass  # 客户端每帧执行
```

---

## 固定频率调度

```python
class SaveSystem(ServerSubsystem):

    def onInit(self):
        self.scheduleFixed('save', period=10)  # 每 10 秒执行

    @Sched.Fixed('save')
    def auto_save(self):
        print('保存数据...')

    def onDestroy(self):
        self.stopFixed('save')
```

---

## 事件触发调度

```python
class BossSystem(ServerSubsystem):

    @Sched.Event('BossSpawned', isCustom=True, scheduleFlag=SchedEventFlags.Event)
    def on_boss_spawn(self):
        print('Boss 出现！开始 AI 逻辑')
```

---

## 底层 Scheduler API

如果不想使用装饰器，也可以直接操作 `Scheduler` 实例：

```python
from architect.core.scheduler import Scheduler

sched = Scheduler()
sched.addTask('Update', my_func)       # 注册任务
sched.addSuspendableTask('Update', my_gen)  # 协程任务
sched.executeSequence()                # 执行一轮
sched.removeTask('Update', task_id)    # 取消任务
```

---

## 异步 Future 与协程

```python
from architect.core.scheduler import Future, Async

@Async
def fetch_data():
    "生成器函数转异步协程。yield 出来的 Future 会被自动等待。"
    result1 = yield remote.client.invoke('Server.check_login')
    result2 = yield remote.client.invoke('Server.get_profile')
    return result1, result2

# 调用
ftr = fetch_data()
ftr.done(lambda data: print('获取完成:', data))
ftr.expected(lambda err: print('失败:', err))
```

---

## 重入保护

如果上一个 `executeSequence` 还未完成（某任务耗时超过一个 Tick），当前帧**直接跳过**并递增内部计数器。

```python
sched.getSkippedUpdates()  # 返回跳过帧数（通过 Profiler 可观测）
```

这不是 Bug——跳帧是单线程环境下的止损策略（排队会导致无限堆积）。跳过帧数通过 Profiler 的 `scheduler.tickSkipped` 指标暴露，开发者可以据此识别性能瓶颈。