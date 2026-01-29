# `architect.scheduler` 模块

任务调度器，实现延迟任务、定时任务及任务队列管理。

源文件： `architect/scheduler.py`

主要类型与说明：

- `Task` — 基本任务封装，包含 `fn`, `id`, `finished`
- `SuspendableTask` — 支持生成器（协程式）任务，通过 `callOnce()` 恢复执行直到完成

- `Scheduler` — 任务调度核心
	- `addTask(scheduleName, fn)` / `addSuspendableTask(scheduleName, generator)` — 注册任务
	- `execute(scheduleName)` / `executeSequence()` — 执行单个队列或预定义顺序（`BeforeUpdate`, `Update`, `AfterUpdate`）
	- `runTimer(fn, ticks=1, interval=False)` — 按 ticks 延迟执行/定时执行
	- `executeAsync` / `executeSequenceAsync` — 异步执行（封装为 `Future`）

- `Future` — 简单的线程封装，用于异步执行并等待结果（`runAsync` 返回 `Future`）

使用建议：`Scheduler` 适合将独立任务分发到不同执行阶段，或将长耗时任务放入 `Future` / `SuspendableTask` 避免阻塞主循环。
