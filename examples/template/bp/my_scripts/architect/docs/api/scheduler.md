# Scheduler API

`architect.scheduler` 模块提供了灵活的任务调度机制，支持基于帧、Tick 和固定间隔的任务执行，并集成了一系列用于管理这些任务的类和函数。

## `Scheduler` 类

`Scheduler` 类是框架核心调度逻辑的实现，负责管理和执行各种类型的任务。

### 构造函数

#### `Scheduler()`

初始化一个新的调度器实例。

### 方法

#### `execute(scheduleFlag, args=[])`

执行指定调度标志下的所有任务。

- **`scheduleFlag`**: (字符串) 调度标志，例如 `SchedUpdateFlags.Update`。
- **`args`**: (列表 `list`) 传递给任务函数的参数列表。

#### `addTask(scheduleFlag, fn)`

添加一个普通任务（函数）。

- **`scheduleFlag`**: (字符串) 调度标志。
- **`fn`**: (函数 `FunctionType`) 要添加的任务函数。
- **返回值**: (整数 `int`) 任务的 ID。

#### `addSuspendableTask(scheduleFlag, generator)`

添加一个可挂起任务（生成器）。

- **`scheduleFlag`**: (字符串) 调度标志。
- **`generator`**: (生成器 `GeneratorType`) 要添加的生成器任务。
- **返回值**: (整数 `int`) 任务的 ID。

#### `removeTask(scheduleFlag, taskId=-1)`

移除指定调度标志下的任务。如果 `taskId` 为 `-1`，则移除该调度标志下的所有任务。

- **`scheduleFlag`**: (字符串) 调度标志。
- **`taskId`**: (整数 `int`, 默认值 `-1`) 要移除的任务 ID。

#### `executeSequence(*args)`

按照预定义的顺序（`BeforeUpdate`, `Update`, `AfterUpdate`）执行所有调度队列中的任务。

- **`args`**: 传递给任务函数的参数列表。
- **返回值**: (元组 `tuple[float, int]`) `(deltaTime, skippedUpdates)`，表示自上次执行以来的时间差和跳过的更新次数。

#### `addPeriodicTask(fn, ticks=1, interval=False)`

添加一个周期性任务。

- **`fn`**: (函数 `FunctionType`) 任务函数。
- **`ticks`**: (整数 `int`, 默认值 `1`) 任务执行的周期（以 tick 计）。
- **`interval`**: (布尔值 `bool`, 默认值 `False`) 如果为 `True`，则任务会重复执行；如果为 `False`，则只执行一次。
- **返回值**: (整数 `int`) 任务的 ID。

#### `runTimeout(fn, ticks=1)`

延迟指定 `ticks` 数后执行一次任务。

- **`fn`**: (函数 `FunctionType`) 任务函数。
- **`ticks`**: (整数 `int`, 默认值 `1`) 延迟的 tick 数。
- **返回值**: (整数 `int`) 任务的 ID。

#### `runInterval(fn, ticks=1)`

每隔指定 `ticks` 数循环执行任务。

- **`fn`**: (函数 `FunctionType`) 任务函数。
- **`ticks`**: (整数 `int`, 默认值 `1`) 间隔的 tick 数。
- **返回值**: (整数 `int`) 任务的 ID。

#### `run(fn)`

在下一个可用周期执行一次任务。

- **`fn`**: (函数 `FunctionType`) 任务函数。
- **返回值**: (整数 `int`) 任务的 ID。

#### `clearTimeout(taskId)`

取消通过 `addPeriodicTask` 或 `runTimeout` 添加的任务。

- **`taskId`**: (整数 `int`) 要取消的任务 ID。

## `Task` 类 (内部工具)

封装了一个普通函数任务的类。

### 属性

- **`fn`**: 任务函数。
- **`id`**: 任务的唯一 ID。
- **`finished`**: (布尔值) 任务是否已完成。

## `SuspendableTask` 类 (内部工具)

封装了一个生成器任务的类，支持任务的挂起和恢复。

### 属性

- **`fn`**: 生成器函数。
- **`gen`**: 生成器实例。
- **`id`**: 任务的唯一 ID。
- **`finished`**: (布尔值) 任务是否已完成。

### 方法

#### `callOnce()`

执行生成器任务的下一步。如果任务完成，则设置 `finished` 为 `True`。

## `TimerAdapter` 类

一个适配器类，用于将 `AddRepeatedTimer` 和 `CancelTimer` 引擎 API 封装成可控的定时器对象。

### 构造函数

#### `TimerAdapter(period, fn)`

- **`period`**: (浮点数 `float`) 定时器周期（秒）。
- **`fn`**: (函数 `FunctionType`) 定时器触发时执行的函数。

### 方法

#### `start()`

启动定时器。

#### `cancel()`

取消定时器。

## `SchedulerPoller` 类

一个封装了 `Scheduler` 和 `TimerAdapter` 的类，用于以固定频率驱动 `Scheduler` 的 `executeSequence` 方法。

### 构造函数

#### `SchedulerPoller(scheduler, period=1)`

- **`scheduler`**: (`Scheduler` 实例) 要驱动的调度器。
- **`period`**: (浮点数 `float`, 默认值 `1`) 驱动调度器的周期（秒）。

### 方法

#### `start()`

启动调度器轮询。

#### `cancel()`

取消调度器轮询。

## `SimpleFixedScheduler` 类

继承自 `SchedulerPoller`，是一个简化的固定频率调度器，内部会自动创建一个 `Scheduler` 实例。

### 构造函数

#### `SimpleFixedScheduler(period=1)`

- **`period`**: (浮点数 `float`, 默认值 `1`) 调度器的周期（秒）。

## `Sched` 类

一个静态工具类，提供装饰器以简化任务注册。

### 静态属性

- **`TYPE_TICK`**: (整数) Tick 类型调度的内部标识。
- **`TYPE_RENDER`**: (整数) 渲染类型调度的内部标识。
- **`TYPE_FIXED`**: (整数) 固定频率类型调度的内部标识。
- **`TYPE_EVENT`**: (整数) 事件类型调度的内部标识。

### 静态方法 (装饰器)

#### `@staticmethod
def Tick(scheduleFlag=SchedUpdateFlags.Update)`

将方法标记为每 Tick 执行一次的任务。

- **`scheduleFlag`**: (字符串, 默认值 `SchedUpdateFlags.Update`) 调度阶段标志。

#### `@staticmethod
def Render(scheduleFlag=SchedUpdateFlags.Update)`

将方法标记为每渲染帧执行一次的任务（仅限客户端）。

- **`scheduleFlag`**: (字符串, 默认值 `SchedUpdateFlags.Update`) 调度阶段标志。

#### `@staticmethod
def Fixed(schedulerName, scheduleFlag=TIMER_TASK)`

将方法标记为固定频率任务，需要配合 `Subsystem.scheduleFixed(name, interval)` 启动。

- **`schedulerName`**: (字符串) 调度器的名称。
- **`scheduleFlag`**: (字符串, 默认值 `TIMER_TASK`) 调度阶段标志。

#### `@staticmethod
def Event(eventType, isCustom=False, scheduleFlag=SchedEventFlags.Event)`

将方法标记为在特定事件触发时执行的任务。

- **`eventType`**: (字符串) 事件类型名称。
- **`isCustom`**: (布尔值, 默认值 `False`) 是否为自定义事件。
- **`scheduleFlag`**: (字符串, 默认值 `SchedEventFlags.Event`) 事件调度阶段标志。

## 全局函数

#### `addTimer(period, fn)`

注册一个重复执行的定时器。

- **`period`**: (浮点数 `float`) 定时器周期（秒）。
- **`fn`**: (函数 `FunctionType`) 定时器触发时执行的函数。
- **返回值**: 定时器 ID。

#### `cancelTimer(timer)`

取消一个已注册的定时器。

- **`timer`**: 定时器 ID。
