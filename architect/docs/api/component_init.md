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

## `ClientComponent` 类

`ClientComponent` 是客户端组件的基类，继承自 `clientApi.GetComponentCls()`（网易引擎的客户端组件基类）。

### 方法

#### `onCreate(self, entityId)`

组件创建时调用。

- **`entityId`**: (字符串) 组件所属的实体 ID。

#### `loadData(self, entityId)`

组件加载数据时调用。

- **`entityId`**: (字符串) 组件所属的实体 ID。

## `ServerComponent` 类

`ServerComponent` 是服务端组件的基类，继承自 `serverApi.GetComponentCls()`（网易引擎的服务端组件基类）。

### 方法

#### `onCreate(self, entityId)`

组件创建时调用。

- **`entityId`**: (字符串) 组件所属的实体 ID。

#### `loadData(self, entityId)`

组件加载数据时调用。

- **`entityId`**: (字符串) 组件所属的实体 ID。

## 使用示例

```python
from ..architect.component import Component, createComponent, getComponent

# 定义一个自定义组件
class MyComponent(Component):
    def __init__(self):
        self.some_data = 0

# 创建组件
entity_id = "player_123"
comp = createComponent(entity_id, MyComponent)

# 获取组件
comp = getComponent(entity_id, MyComponent)
```
