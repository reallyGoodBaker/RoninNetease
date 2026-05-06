# 属性通用 (Attr Common) API

`architect.attr.common` 模块定义了属性系统使用的事件常量和基类。

## `ClientAttrEvents` 类

定义了客户端属性相关的事件名称。

### 静态属性

- **`AttrChange`**: (字符串) 客户端属性值变更事件的名称。值为 `_attr_change_`。
- **`ServerSync`**: (字符串) 客户端向服务器同步属性事件的名称。值为 `_attr_sync_`。

## `ServerAttrEvents` 类

定义了服务器端属性相关的事件名称。

### 静态属性

- **`AttrChange`**: (字符串) 服务器属性值变更事件的名称。值为 `_attr_change_`。
- **`ClientSync`**: (字符串) 服务器向客户端同步属性事件的名称。值为 `_attr_sync_`。

## `ReactiveDepEvents` 类

定义了响应式属性依赖事件的类型。

### 静态属性

- **`Get`**: (整数) 获取属性值时的事件类型。值为 `0`。
- **`Set`**: (整数) 设置属性值时的事件类型。值为 `1`。

## `ReactiveBase` 类

`ReactiveBase` 是所有响应式属性的基类，提供了基本的属性存储和事件触发机制。

### 构造函数

#### `ReactiveBase(entityId, name, defaultValue=None)`

- **`entityId`**: (字符串) 属性所属的实体 ID。
- **`name`**: (字符串) 属性的名称。
- **`defaultValue`**: (任意类型, 默认值 `None`) 属性的默认值。

### 属性

#### `value`

- **类型**: 任意类型
- **说明**: 属性的当前值。通过 `@property` 实现读写。每次访问会触发 `ReactiveDepEvents.Get` 事件，每次设置会触发 `ReactiveDepEvents.Set` 事件。

#### `oldValue`

- **类型**: 任意类型
- **说明**: 属性上一次的值。在 `value` 被设置前存储。

### 方法

#### `onDepEvent(self, evType)`

依赖事件回调。当属性的 `value` 被访问或修改时，此方法会被调用。

- **`evType`**: (整数) 触发的依赖事件类型（`ReactiveDepEvents.Get` 或 `ReactiveDepEvents.Set`）。
