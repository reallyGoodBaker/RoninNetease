# `architect` 模块概览

该文档列出 `architect` 包下的主要模块及简要说明。

- `architect/annotation.py` — 注解辅助工具
- `architect/basic.py` — 基本工具与启动逻辑
- `architect/localActor.py` — 本地 Actor 支持
- `architect/profiler.py` — 性能分析工具
- `architect/ref.py` — 引用与资源管理
- `architect/remoteStore.py` — 远程存储接口
- `architect/scheduler.py` — 任务调度器
- `architect/subsystem.py` — 子系统管理器（核心）
- `architect/unreliable.py` — 非可靠传输/任务支持
- `architect/component/index.py` — 组件注册与实体管理
- `architect/event/*.py` — 事件系统（client/server/core）
- `architect/fsm/deprecated.py` — 状态机（已弃用）
- `architect/level/*.py` — 关卡（client/server）接口
- `architect/math/*.py` — 数学工具（vec3, mat4 等）
- `architect/persistent/*.py` — 持久化相关
- `architect/query/*.py` — 查询缓存与查询处理
- `architect/utils/*.py` — 各类工具方法与扩展

更多细节请查看对应模块的文档（例如 `docs/architect/subsystem.md`）。
