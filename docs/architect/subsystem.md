# `architect.subsystem` 说明

该模块实现子系统注册、初始化与事件循环。

主要类与功能：

- `SubsystemManager` — 管理已注册子系统、创建 Client/Server 系统、调度 Tick 与事件监听。
- `Subsystem` — 子系统基类，常用钩子方法：`onInit()`, `onReady()`, `onUpdate(dt)`, `onRender(dt)`, `onDestroy()`。
- `ServerSubsystem` / `ClientSubsystem` — 分别为服务端与客户端子系统的扩展接口。

执行顺序（重要）：

1. 子系统被创建后，会在 `_init()` 中调用 `onInit()`；也就是说，`onInit` 在单个子系统创建完成后立即执行。
2. 当所有注册的子系统都创建完毕后，`appendAllSubsystems()` 会在结尾处遍历并调用每个子系统的 `onReady()`；因此 `onReady` 在所有子系统初始化完毕后执行。

这意味着：如果你的子系统需要依赖其它子系统（通过 `getSubsystem()` 获取），请把依赖逻辑放在 `onReady()` 中；而 `onInit()` 适合做本子系统的本地初始化。

参见实现：`architect/subsystem.py`（查看 `_init()`、`appendAllSubsystems()` 的实现以获得更详细线索）。

主要类/方法一览：

- `EventListener(evType, fn)` — 简单的事件监听器封装对象

- `SubsystemManager`（静态与实例方法）
	- `getInst()` : 获取当前运行端（client/server）管理实例
	- `createClientSystem(engine, sysName, clsPath)` / `createServerSystem(...)` : 通过引擎注册管理系统
	- `createClient(cls, engine, sysName)` / `createServer(cls, engine, sysName)` : 为 ShadowSystem 创建管理器
	- `appendAllSubsystems(isServer)` : 创建并初始化已注册的所有子系统，随后启动 ticking 并注册组件
	- `startTicking(isServer)` : 为客户端/服务端注册 tick 与 render 回调事件
	- `addSubsystem(subsystemCls)` / `addSubsystemInst(subsystem)` : 创建子系统或直接添加已有实例（会调用 `_init()`）
	- `getSubsystem(subsystemCls)` / `removeSubsystem(subsystemCls)` : 访问与移除子系统
	- `registerSubsystem(subsystem)` / `unregisterSubsystems()` : 注册/清空待注册子系统列表
	- `tickServer()`, `tickClient()`, `tickRender()` : 定时执行子系统的更新与渲染钩子，并驱动查询调用
	- `addListener(event, fn, isCustomEvent=False)` / `removeListener(event, fn)` : 全局事件监听管理（会在内部封装 `EventListener`）

- `Subsystem`（实例方法）
	- `onUpdate(dt)` : 每 tick 调用（需将 `canTick` 设为 `True` 才会被调用）
	- `onReady()` : 所有子系统创建完毕后的回调，适合做依赖其它子系统的初始化
	- `onInit()` : 当前子系统创建完毕后的回调（早于 `onReady`）
	- `onDestroy()` : 销毁回调
	- `getInstance()` : 静态方法，按类获取已注册的子系统实例
	- `on/off/listen/unlisten` : 事件绑定/解绑的便捷方法（内部使用 `event.client` / `event.server`）

- `ServerSubsystem` / `ClientSubsystem` 扩展
	- `ServerSubsystem.sendAllClients(eventName, eventData)` / `sendClient(...)`：向客户端广播或通知
	- `ServerSubsystem.spawnEntity(...)`, `destroyEntity(...)`, `spawnItem(...)`：实体与物品操作封装
	- `ClientSubsystem.sendServer(eventName, eventData)`：向服务端发送事件
	- `ClientSubsystem.spawnEntity(typeStr, pos, rot)` / `destroyEntity(entityId)` / `createSfx(...)`：客户端实体与特效管理

示例建议：
- 若子系统相互依赖，使用 `onInit()` 做本地初始化，使用 `onReady()` 做跨子系统依赖绑定（通过 `getInstance()` 或 `getSubsystem()` 访问其它子系统）。
