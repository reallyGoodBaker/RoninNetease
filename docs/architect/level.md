# `architect.level` 模块

关卡管理相关接口，包含客户端与服务端的对等实现，用于实体定位、维度管理等。

源文件： `architect/level/client.py`, `architect/level/server.py`

主要类/属性：

- `LevelClient` — 客户端单例，封装对客户端引擎各种子系统的访问句柄
	- 常见属性：`camera`, `game`, `configClient`, `playerView`, `GetScreenSize()`（通过 `game` 获取）
	- 使用：`LevelClient.getInst()` 获取单例实例

- `LevelServer` — 服务端静态对象，直接创建多个引擎句柄作为类属性（如 `game`, `command`, `extraData`, `CreateChunkSource` 等）

说明：`LevelClient` 与 `LevelServer` 提供方便的引擎 API 访问点，其他模块常通过 `LevelClient.getInst()` 或 `LevelServer` 类属性来调用引擎接口。
