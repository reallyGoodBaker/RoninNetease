# 单位转换 (Unit) API

`architect.math.unit` 模块提供了时间单位的常量定义，用于时间转换和计算。

## `time` 类

`time` 类是一个静态类，提供了各种时间单位相对于秒的换算系数。

### 类属性

#### `entityTick`

- **类型**: 浮点数
- **值**: `0.05`
- **说明**: 实体更新周期（秒）。在 Minecraft 中，实体每游戏刻更新一次，1 游戏刻 = 0.05 秒。

#### `tick`

- **类型**: 浮点数
- **值**: `0.0333333333333333` (约 1/30)
- **说明**: 标准游戏刻（秒）。用于一般游戏逻辑更新。

#### `ms`

- **类型**: 浮点数
- **值**: `0.001`
- **说明**: 毫秒（秒）。1 毫秒 = 0.001 秒。

#### `s`

- **类型**: 浮点数
- **值**: `1`
- **说明**: 秒（基准单位）。

#### `m`

- **类型**: 浮点数
- **值**: `60`
- **说明**: 分钟（秒）。1 分钟 = 60 秒。

#### `h`

- **类型**: 浮点数
- **值**: `60 * m` = `3600`
- **说明**: 小时（秒）。1 小时 = 60 分钟 = 3600 秒。

#### `d`

- **类型**: 浮点数
- **值**: `24 * h` = `86400`
- **说明**: 天（秒）。1 天 = 24 小时 = 86400 秒。

#### `w`

- **类型**: 浮点数
- **值**: `7 * d` = `604800`
- **说明**: 周（秒）。1 周 = 7 天 = 604800 秒。

#### `y`

- **类型**: 浮点数
- **值**: `365 * d` = `31536000`
- **说明**: 年（秒）。1 年 = 365 天 = 31536000 秒（不考虑闰年）。

## 使用示例

### 1. 时间单位转换

```python
from ..architect.math.unit import time

# 将秒转换为其他单位
seconds = 120
minutes = seconds / time.m  # 2.0 分钟
hours = seconds / time.h    # 0.0333... 小时
days = seconds / time.d     # 0.001388... 天

# 将其他单位转换为秒
two_minutes = 2 * time.m    # 120 秒
three_hours = 3 * time.h    # 10800 秒
one_week = 1 * time.w       # 604800 秒
```

### 2. 游戏时间计算

```python
from ..architect.math.unit import time

class GameTimer:
    def __init__(self, duration_seconds):
        self.duration = duration_seconds
        self.elapsed = 0
    
    def update(self, delta_time):
        """更新计时器"""
        self.elapsed += delta_time
        
        # 检查是否超时
        if self.elapsed >= self.duration:
            return True
        return False

# 创建 5 秒的计时器
timer = GameTimer(5 * time.s)

# 创建 30 游戏刻的计时器（Minecraft 实体更新）
entity_timer = GameTimer(30 * time.entityTick)  # 30 * 0.05 = 1.5 秒
```

### 3. 动画和效果

```python
from ..architect.math.unit import time

class Animation:
    def __init__(self, duration_ticks):
        # 持续时间以游戏刻为单位
        self.duration_ticks = duration_ticks
        self.duration_seconds = duration_ticks * time.entityTick
        self.progress = 0
    
    def update(self, delta_time):
        # 更新进度（delta_time 以秒为单位）
        self.progress += delta_time / self.duration_seconds
        self.progress = min(self.progress, 1.0)
        
        # 计算当前值（0 到 1）
        return self.progress

# 创建持续 20 游戏刻的动画（1 秒）
animation = Animation(20)  # 20 * 0.05 = 1.0 秒
```

### 4. 冷却时间系统

```python
from ..architect.math.unit import time

class CooldownSystem:
    def __init__(self):
        self.cooldowns = {}  # {skill_name: remaining_time}
    
    def set_cooldown(self, skill_name, cooldown_seconds):
        """设置技能冷却时间"""
        self.cooldowns[skill_name] = cooldown_seconds
    
    def update(self, delta_time):
        """更新所有冷却时间"""
        for skill_name in list(self.cooldowns.keys()):
            self.cooldowns[skill_name] -= delta_time
            if self.cooldowns[skill_name] <= 0:
                del self.cooldowns[skill_name]
    
    def is_ready(self, skill_name):
        """检查技能是否冷却完成"""
        return skill_name not in self.cooldowns

# 使用示例
cooldown_system = CooldownSystem()

# 设置 10 秒冷却
cooldown_system.set_cooldown('fireball', 10 * time.s)

# 设置 5 分钟冷却
cooldown_system.set_cooldown('ultimate', 5 * time.m)

# 设置 1 游戏刻冷却（快速技能）
cooldown_system.set_cooldown('quick_attack', 1 * time.entityTick)
```

## 时间单位关系

```
1 年 (y) = 365 天
1 周 (w) = 7 天
1 天 (d) = 24 小时
1 小时 (h) = 60 分钟
1 分钟 (m) = 60 秒
1 秒 (s) = 1000 毫秒
1 游戏刻 (tick) ≈ 0.0333 秒（30 FPS）
1 实体刻 (entityTick) = 0.05 秒（20 TPS）
```

## 注意事项

1. **基准单位**: 所有时间单位都以秒为基准进行定义。
2. **游戏刻**: `tick` 和 `entityTick` 是不同的：
   - `entityTick` (0.05 秒) 是 Minecraft 实体更新的标准周期（20 TPS）。
   - `tick` (约 0.0333 秒) 是更通用的游戏逻辑更新周期（30 FPS）。
3. **精度**: 使用浮点数表示，可能存在浮点精度误差。
4. **闰年**: `y` 属性使用 365 天，不考虑闰年。如需精确的年计算，请自行处理。
5. **性能**: 这些是常量，访问开销极小，适合频繁使用。

## 扩展使用

### 自定义时间单位

```python
from ..architect.math.unit import time

# 定义自定义时间单位
class CustomTime:
    # 复用现有单位
    second = time.s
    minute = time.m
    hour = time.h
    
    # 自定义单位
    fortnight = 14 * time.d  # 两周
    month = 30 * time.d      # 月（近似）
    quarter = 3 * time.m     # 季度
    decade = 10 * time.y     # 十年

# 使用自定义单位
from CustomTime import CustomTime as ct
two_months = 2 * ct.month    # 60 天
three_quarters = 3 * ct.quarter  # 9 个月
```

### 时间格式化

```python
from ..architect.math.unit import time

def format_duration(seconds):
    """将秒数格式化为可读字符串"""
    if seconds >= time.d:
        days = seconds // time.d
        return f"{days:.1f} 天"
    elif seconds >= time.h:
        hours = seconds // time.h
        return f"{hours:.1f} 小时"
    elif seconds >= time.m:
        minutes = seconds // time.m
        return f"{minutes:.1f} 分钟"
    else:
        return f"{seconds:.1f} 秒"

# 示例
print(format_duration(3600))      # 1.0 小时
print(format_duration(90))        # 1.5 分钟
print(format_duration(86400))     # 1.0 天
```
