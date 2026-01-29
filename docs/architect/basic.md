# `architect.basic` 模块

包含一些基础启动与辅助逻辑，用于项目初始化流程和轻量级工具函数。

源文件： `architect/basic.py`

主要函数与变量：

- `isServer()` -> bool
	- 根据引擎 `GetLocalPlayerId()` 判断当前运行环境是否为服务端

- `getComponentCls()` -> class
	- 返回客户端或服务端的组件基类（根据 `isServer()` 判定）

- `getGoalCls()` -> class
	- 返回自定义目标类（由服务端 API 提供）

- `serverTick()` -> int/float
	- 返回当前服务端 tick 时间（从服务端 API 读取）

- 全局变量：
	- `compServer`, `compClient` — 引擎组件工厂句柄
	- `localPlayer` — 本地玩家 ID（仅客户端可用）
	- `defaultFilters` — 示例过滤器结构（JSON-like），用于查询/筛选

备注：本模块主要对引擎 API 做一层轻量封装，方便上层模块统一使用。
