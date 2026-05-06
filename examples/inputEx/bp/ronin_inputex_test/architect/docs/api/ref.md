# Ref API

`architect.ref` 模块提供了一个简单的 `Ref` 类，用于封装可变值，方便在需要引用传递或在闭包中修改外部变量时使用。

## `Ref` 类

`Ref` 类是一个简单的包装器，可以包含任意值，并通过 `value` 属性进行访问和修改。

### 构造函数

#### `Ref(value)`

- **`value`**: (任意类型) 要封装的初始值。

### 属性

#### `value`

- **类型**: 任意类型
- **说明**: 封装的值。可以通过 `ref_instance.value` 获取或设置。

```python
from ..architect.ref import Ref

my_ref = Ref(10)
print(my_ref.value) # 输出: 10

my_ref.value = 20
print(my_ref.value) # 输出: 20
```

### 方法

#### `isValid()`

检查 `Ref` 封装的值是否不为 `None`。

- **返回值**: (布尔值 `bool`) 如果 `value` 不为 `None` 则返回 `True`，否则返回 `False`。

```python
empty_ref = Ref(None)
print(empty_ref.isValid()) # 输出: False

valid_ref = Ref("hello")
print(valid_ref.isValid()) # 输出: True
```
