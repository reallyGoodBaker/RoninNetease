# Architect 框架文档

`architect` 是一个专为《我的世界》中国版（网易版）模组开发设计的模块化、响应式框架。它通过解耦逻辑与数据，极大地提升了大型模组的开发效率和代码可维护性。

## 核心概念

框架围绕以下几个核心模块展开，点击链接查看详细文档：

1.  **[子系统 (Subsystem)](docs/subsystem.md)**: 业务逻辑的载体，负责模块化管理和生命周期控制。
2.  **[事件系统 (Event)](docs/event.md)**: 基于装饰器的事件监听机制，简化引擎与自定义事件的处理。
3.  **[调度系统 (Scheduler)](docs/scheduler.md)**: 提供 Tick、渲染帧、固定频率及基于协程的任务调度。
4.  **[组件系统 (ECS)](docs/ecs.md)**: 实体组件系统实现，通过 `@Query` 自动注入数据实例。
5.  **[UI 系统 (UiSubsystem)](docs/ui.md)**: 集成响应式数据绑定 (Signal/Sink) 的 UI 管理方案。
6.  **[工具与扩展 (Utils)](docs/utils.md)**: 数学库 (vec3/mat4)、FSM、持久化及常用引擎 API 封装。

---

## 快速开始

在模组的 `modMain.py` 中引入并初始化框架：

```python
# bp/wstudio_invincible_scripts/modMain.py

from .architect.subsystem import createServer, createClient

# 初始化服务端
createServer('namespace', 'system_name')

# 初始化客户端 (建议指定入口模块以触发自动注册)
createClient('namespace', 'system_name', 'subclient.index')
```

---

## 开发规范

1.  **模块化**: 尽量将独立的逻辑拆分为不同的子系统（Subsystem）。
2.  **数据分离**: 使用组件（Component）存储状态，而非在子系统中直接定义大量变量。
3.  **响应式 UI**: 在 UI 开发中优先使用 `signal` 和 `Sink`，避免手动操作复杂的控件刷新逻辑。
