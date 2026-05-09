# Basic API

`architect.basic` 模块提供了一些基础的工具类和函数，用于判断运行环境、封装位置信息以及访问引擎组件工厂。

## `Location` 类

`Location` 类用于封装实体的三维位置和维度信息。

### 构造函数

#### `Location(pos, dim)`

- **`pos`**: (元组 `tuple[float, float, float]`) 实体的三维坐标。
- **`dim`**: (整数 `int`) 实体所在的维度 ID。

### 属性

- **`pos`**: (元组) 实体的三维坐标。
- **`dim`**: (整数) 实体所在的维度 ID。

## 函数

#### `isServer()`

判断当前代码是否运行在服务端。

- **返回值**: (布尔值 `bool`) 如果是服务端则返回 `True`，否则返回 `False`。

#### `getComponentCls()`

获取当前运行环境（客户端或服务端）的引擎组件基类。

- **返回值**: (类 `class`) 引擎组件基类（`mod.client.extraClientApi.GetComponentCls()` 或 `mod.server.extraServerApi.GetComponentCls()`）。

#### `getGoalCls()`

获取服务端的自定义目标（Goal）基类。

- **返回值**: (类 `class`) `mod.server.extraServerApi.GetCustomGoalCls()`。

#### `serverTick()`

获取当前服务器的 tick 时间。

- **返回值**: (浮点数 `float`) 服务器当前的 tick 时间。

## 全局变量

#### `compServer`

服务端引擎组件工厂实例，等同于 `mod.server.extraServerApi.GetEngineCompFactory()`。

#### `compClient`

客户端引擎组件工厂实例，等同于 `mod.client.extraClientApi.GetEngineCompFactory()`。

#### `localPlayer`

客户端本地玩家的 ID。**注意：不应在服务端使用此变量。**

#### `defaultFilters`

一个默认的实体筛选器字典，用于 `GetEntitiesAround` 等方法，筛选玩家或 Mob 实体。

```python
defaultFilters = {
    "any_of": [
        {
            "subject" : "other",
            "test" :  "is_family",
            "value" :  "player"
        },
        {
            "subject" : "other",
            "test" :  "is_family",
            "value" :  "mob"
        }
    ]
}
```
