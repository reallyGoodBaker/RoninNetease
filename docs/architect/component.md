# `architect.component` 模块

组件注册与实体管理入口。核心文件为 `component/index.py`，负责组件生命周期与实体集合管理。

源文件： `architect/component/index.py`

主要常量/函数/类：

- `COMPONENT_NAMESPACE` — 注册组件时使用的命名空间常量
- `Component(persist=False)` — 装饰器，用于标记类为组件并注册到客户端或服务端组件列表

- `registerComponents(isServer)` — 将已标记组件注册到引擎（根据 `isServer` 选择 server/client API）

- `getComponentAnnotation(cls)` / `isPersistComponent(cls)` — 读取组件注解并判断是否为持久组件

- `createComponent(entityId, cls)` — 创建实体组件并执行 `onCreate`、`loadData` 等初始化逻辑
- `destroyComponent(entityId, cls)` — 销毁实体上的组件并维护内部计数
- `getOneComponent(entityId, cls)` / `getComponent(entityId, clsList, filter=None)` — 获取实体上的组件实例
- `getComponentWithQuery(entityId, targets, required=[], excluded=[])` — 带查询条件的组件获取辅助函数
- `getEntities()` — 返回当前已注册实体 ID 列表

- `BaseCompServer` / `BaseCompClient` — 分别继承引擎组件基类的空实现，提供 `onCreate` 与 `loadData` 钩子示例

使用提示：
- 对于需要持久化的组件，使用 `@Component(persist=True)` 标记，并在组件类实现 `loadData`/`saveData`（如引擎 API 支持）
