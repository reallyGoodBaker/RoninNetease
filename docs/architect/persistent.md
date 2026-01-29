# `architect.persistent` 模块

持久化相关模块，封装客户端/服务端的数据持久化与存取逻辑。

源文件： `architect/persistent/client.py`, `architect/persistent/server.py`, `architect/persistent/common.py`

主要类/接口：

- `DBSource`（接口） — 定义 `getData` / `setData` / `removeData` / `clearData` 等方法
- `DatabaseView` / `DatabaseArrayView` — 基于 `DBSource` 的视图封装，提供 `get`/`set`/`batch` 等便捷方法，自动写回底层存储

`persistent/client.py`:
- `ClientKVDatabase` / `ClientKVDatabaseGlobal` — 客户端的键值存储实现，基于 `LevelClient.configClient` 的配置存储
	- 方法：`getData(key)`, `setData(key, value)`, `removeData(key)`, `clearData()`

`persistent/server.py`:
- `ServerKVDatabase` — 服务端的键值存储实现，使用 `LevelServer.extraData` 保存数据
	- 方法：`getData(key)`, `setData(key, value)`, `removeData(key)`, `clearData()`

使用建议：使用 `DBSource.createView` 或 `createArrayView` 获取视图对特定键进行局部读写操作，避免频繁直接操作底层存储结构。
