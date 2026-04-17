# 组件模块 (`__init__.py`)

`architect.component.__init__.py` 是组件系统的入口模块，它导出了核心组件类和常用函数，并定义了客户端和服务端组件的基础类。

## 导入的模块

该模块从 `.core` 和 `.common` 子模块导入了以下内容：

- **从 `.core` 导入**:
  - `Component`: 组件基类。
  - `_registerCompsIntoGame`: 内部函数，用于将组件注册到游戏引擎。
  - `getComponent`, `getComponentAnnotation`, `getEntities`, `isPersistComponent`, `createComponent`, `createSingletonComponent`, `destroyComponent`, `getOneComponent`, `getComponentWithQuery`, `getOrCreateComponent`, `getOrCreateSingletonComponent`, `getOneSingletonComponent`, `hasComponent`, `removeComponents`: 组件操作函数。
  - `BaseCompClient`, `BaseCompServer`: 客户端和服务端组件的基础类。

- **从 `.common` 导入**:
  - `NeC`, `NeS`: 组件命名空间常量。