# `architect.event` 模块

事件系统的文档概览，包含客户端与服务端事件实现：

- `architect/event/client.py` — 客户端事件封装
- `architect/event/server.py` — 服务端事件封装
- `architect/event/core.py` — 事件核心实现

事件用于子系统间解耦通知与广播。

核心实现（`event/core.py`）主要类/接口：

- `Delegate` — 基于 `Unreliable` 的委托封装
	- `bind(fn)` / `unbind()` / `call(*args)`：绑定与调用目标函数

- `EventSignal` — 简单事件信号，管理多个回调
	- `on(fn)` / `off(fn)` / `emit(*args)`

- `EventTarget` — 事件目标容器
	- `addListener(event, fn)` / `removeListener(event, fn)` / `dispatch(event, *args)`

- `ChainedEvent` — 链式事件对象
	- `stop()`：停止事件传递
	- `prevent()`：阻止默认行为（设置 `cancel`）
	- `dict()` / `setEvent(p, v)`：访问与修改内部数据

- `EventChain` — 顺序触发监听器（支持捕获/冒泡/中断）
	- `capture(fn)` / `addListener(fn)` / `removeListener(fn)` ：添加/移除监听器
	- `dispatch(evType, _ev)`：触发事件，支持 `stop()` 和 `guarded`（在监听器出错时停止后续执行）

这些工具为上层的 `event.client` / `event.server` 提供可组合的事件分发与守护调用机制。
