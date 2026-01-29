# `architect.utils` 模块

通用工具集合，包含 server 工具、molang 支持、扩展集合（如 list）以及 persona 相关逻辑。

子模块：

- `utils/server.py`
- `utils/enhance/list.py`
- `utils/molang/*`
- `utils/persona/*`

源文件： `architect/utils` 目录下的多个文件

子模块详细说明：

`utils/server.py`:
- `runCommand(cmd, entityId)` — 在服务端执行命令（通过 `LevelServer.command`）
- `motion(entityId, mot)` — 根据实体类型设置运动（玩家/普通实体）
- `sound(entityId, sound)` — 播放声音（封装为 command）
- `particle(particle, pos)` — 在指定位置生成粒子（通过 command）

`utils/enhance/list.py`:
- `remove(list, item)` — 从列表中移除元素并返回成功标志
- `chunk(list, size)` — 将列表切分为块
- `flatten(list)` — 扁平化嵌套列表
- `compact(list)` — 过滤掉 falsy 值
- `fill(list, item, start=0, end=None)` — 在区间内用同一值填充
- `without(list, item)` — 返回不包含指定元素的新列表

`utils/molang`:
- `types.py` — `MolangReadable`, `MolangMutable` 接口定义
- `common.py` — `NamedVariable`, `NamedVariable.getValue/setValue`：访问 Molang 变量的通用实现
- `client.py` — `QueryVariable`, `ReactiveQueryVariable`, `MolangClient`（带 `onRender` 更新），`MolangQuery` 装饰器，用于声明反应式查询变量
- `server.py` — `NamedProperty`, `MolangServer`（负责在服务端广播/转发 molang 查询）

`utils/persona`:
- `client.py` — `PersonaRendererComponent`（`ClientComponent` 的实现），`PersonaEventsSubsystem`（处理来自服务端的 persona 变更事件）
- `server.py` — `PersonaServer`（服务端接口，用于向客户端广播 persona 更改、重置等）

使用建议：`molang` 子模块提供可在客户端/服务端注册、广播和反应式更新的 Molang 查询变量接口；`persona` 子模块封装实体渲染配置与同步。
