# 双精度数学运算 (Double Math) API

`architect.math.double` 模块提供了双精度浮点数的数学运算函数，包括插值、限制和平滑函数。

## 函数

### `lerp(a, b, t)`

线性插值函数。

- **`a`**: (浮点数) 起始值。
- **`b`**: (浮点数) 结束值。
- **`t`**: (浮点数) 插值因子，范围 [0, 1]。
- **返回值**: (浮点数) 插值结果。

**公式**: `a * (1 - t) + b * t`

**示例**:
```python
from ..architect.math.double import lerp

# 在 0 和 10 之间插值
result = lerp(0, 10, 0.5)  # 返回 5.0
result = lerp(0, 10, 0.2)  # 返回 2.0
result = lerp(0, 10, 0.8)  # 返回 8.0
```

### `clamp(x, min, max)`

限制函数，将值限制在指定范围内。

- **`x`**: (浮点数) 输入值。
- **`min`**: (浮点数) 最小值。
- **`max`**: (浮点数) 最大值。
- **返回值**: (浮点数) 限制后的值。

**逻辑**:
- 如果 `x < min`，返回 `min`
- 如果 `x > max`，返回 `max`
- 否则返回 `x`

**示例**:
```python
from ..architect.math.double import clamp

# 限制在 0 到 1 之间
result = clamp(0.5, 0, 1)   # 返回 0.5
result = clamp(-0.5, 0, 1)  # 返回 0.0
result = clamp(1.5, 0, 1)   # 返回 1.0
```

### `smoothstep(edge0, edge1, x)`

平滑步进函数，提供平滑的插值过渡。

- **`edge0`**: (浮点数) 下边界。
- **`edge1`**: (浮点数) 上边界。
- **`x`**: (浮点数) 输入值。
- **返回值**: (浮点数) 平滑插值结果，范围 [0, 1]。

**公式**:
1. 首先将 `x` 归一化到 [0, 1] 范围：`t = clamp((x - edge0) / (edge1 - edge0), 0, 1)`
2. 然后应用平滑函数：`t * t * (3 - 2 * t)`

**特性**:
- 当 `x <= edge0` 时，返回 0
- 当 `x >= edge1` 时，返回 1
- 在 `edge0` 和 `edge1` 之间提供平滑的 S 形过渡

**示例**:
```python
from ..architect.math.double import smoothstep

# 平滑过渡
result = smoothstep(0, 10, 5)   # 返回 0.5
result = smoothstep(0, 10, 2)   # 返回 0.104
result = smoothstep(0, 10, 8)   # 返回 0.896
result = smoothstep(0, 10, -5)  # 返回 0.0
result = smoothstep(0, 10, 15)  # 返回 1.0
```

## 使用示例

### 1. 动画插值

```python
from ..architect.math.double import lerp, smoothstep

class Animation:
    def __init__(self, start_value, end_value, duration):
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.elapsed_time = 0
    
    def update(self, delta_time):
        self.elapsed_time += delta_time
        t = self.elapsed_time / self.duration
        
        # 使用线性插值
        # value = lerp(self.start_value, self.end_value, t)
        
        # 使用平滑插值（更自然）
        smooth_t = smoothstep(0, 1, t)
        value = lerp(self.start_value, self.end_value, smooth_t)
        
        return value
```

### 2. 物理模拟

```python
from ..architect.math.double import clamp

class PhysicsObject:
    def __init__(self, position, velocity, bounds):
        self.position = position
        self.velocity = velocity
        self.bounds = bounds  # (min_x, max_x, min_y, max_y)
    
    def update(self, delta_time):
        # 更新位置
        self.position += self.velocity * delta_time
        
        # 限制在边界内
        min_x, max_x, min_y, max_y = self.bounds
        self.position.x = clamp(self.position.x, min_x, max_x)
        self.position.y = clamp(self.position.y, min_y, max_y)
        
        # 如果碰到边界，反转速度
        if self.position.x <= min_x or self.position.x >= max_x:
            self.velocity.x *= -0.8  # 弹性碰撞
        if self.position.y <= min_y or self.position.y >= max_y:
            self.velocity.y *= -0.8
```

### 3. UI 动画

```python
from ..architect.math.double import lerp, smoothstep

class UIElement:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.animation_progress = 0
    
    def animate_to_target(self, speed):
        # 更新动画进度
        self.animation_progress = min(self.animation_progress + speed, 1.0)
        
        # 使用平滑插值
        smooth_progress = smoothstep(0, 1, self.animation_progress)
        
        # 插值位置
        self.x = lerp(self.x, self.target_x, smooth_progress)
        self.y = lerp(self.y, self.target_y, smooth_progress)
```

## 数学原理

### 线性插值 (Linear Interpolation)

线性插值是最简单的插值方法，在两个值之间按比例计算中间值。公式为：

```
lerp(a, b, t) = a * (1 - t) + b * t
```

### 平滑步进 (Smoothstep)

平滑步进函数提供平滑的 S 形过渡，避免线性插值的突变。其导数是连续的，使得动画更加自然。公式为：

```
smoothstep(edge0, edge1, x) = 
    let t = clamp((x - edge0) / (edge1 - edge0), 0, 1)
    in t * t * (3 - 2 * t)
```

该函数是三次多项式，在边界处的一阶导数为零，确保平滑过渡。

## 注意事项

1. **浮点精度**: 这些函数使用双精度浮点数，适用于大多数游戏计算。
2. **参数范围**: `lerp` 和 `smoothstep` 的 `t` 参数通常应在 [0, 1] 范围内，但函数也能处理超出范围的值。
3. **性能**: 这些函数计算简单，性能开销小，适合每帧调用。
4. **边界条件**: `clamp` 函数要求 `min <= max`，否则可能产生意外结果。
5. **平滑函数**: `smoothstep` 在 `edge0 == edge1` 时会出现除以零错误，使用前应确保边界有效。
