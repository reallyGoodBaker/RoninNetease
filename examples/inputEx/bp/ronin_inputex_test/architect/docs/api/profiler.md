# Profiler API

`architect.profiler` 模块提供了一个简单的装饰器，用于测量函数执行的时间开销。

## `TimeCost` 装饰器

`TimeCost` 是一个函数装饰器，用于计算被装饰函数的执行时间并在控制台打印结果。

### 用法

将 `@TimeCost` 放在你想要测量执行时间的函数上方。

```python
from ..architect.profiler import TimeCost

class MyClass:
    @TimeCost
    def my_function(self, arg1, arg2):
        # 耗时操作
        import time
        time.sleep(1)
        return arg1 + arg2

# 调用函数时会打印执行时间
instance = MyClass()
result = instance.my_function(1, 2)
# 控制台输出类似：Time cost: 1.00xxxx s
```

### 参数

该装饰器不接受参数。

### 返回值

被装饰函数原本的返回值。
