# `architect.unreliable` 模块

实现不可靠传输或不保证交付的任务机制，适用于可丢失但性能敏感的场景。

源文件： `architect/unreliable.py`

核心类：

- `Unreliable` — 提供受保护的调用包装与错误处理机制
	- `_defaultErrorHandler(err)` — 静态默认错误处理器，打印堆栈
	- `onError(fn)` — 设置自定义错误处理器
	- `_handleError(err)` — 内部捕获并调用错误处理器，返回 `(None, err)`
	- `tryCall(fn, *args)` — 尝试调用 `fn`，并在异常时通过 `_handleError` 处理

用途说明：`Unreliable` 不是网络不可靠的意思，而是用于在调用外部/不可信代码时提供错误守护，避免异常中断调用链。
