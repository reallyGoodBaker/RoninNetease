# Profiler — 性能诊断器

`Profiler` 是一个轻量级耗时收集器，用于诊断子系统 `onUpdate`/`onRender` 及各调度器的性能开销。框架提供了一个全局 `profiler` 单例供所有模块共用。

---

## 1. 概述

`Profiler` 的核心功能：

- **耗时记录**：通过 `with profiler.record('key')` 上下文管理器自动计时
- **统计快照**：输出 `avg_ms`（平均耗时）、`max_ms`（最大耗时）、`count`（采样数）
- **全局单例**：`from architect.core.profiler import profiler` 即可使用
- **自动记录**：框架自动将调度器跳过帧数（`scheduler.tickSkipped`、`scheduler.renderSkipped`）写入 profiler

---

## 2. API

### 2.1 `Profiler` 类

| 方法 | 签名 | 说明 |
|---|---|---|
| `enable()` | `() -> None` | 启用 profiler |
| `disable()` | `() -> None` | 禁用 profiler（停止记录） |
| `record(key)` | `(str) -> _TimerContext` | 返回上下文管理器，`with` 块内自动计时 |
| `flush()` | `() -> dict` | 返回统计快照并**重置**所有记录 |
| `snapshot()` | `() -> dict` | 返回统计快照但**不重置**记录 |

### 2.2 全局单例

```python
from architect.core.profiler import profiler

# profiler 是 Profiler 的全局实例
```

### 2.3 返回格式

```python
{
    'key_name': {
        'avg_ms': 1.23,    # 平均耗时（毫秒）
        'max_ms': 5.67,    # 最大耗时（毫秒）
        'count': 120       # 采样次数
    },
    ...
}
```

---

## 3. 使用示例

### 3.1 手动记录耗时

```python
from architect.core.profiler import profiler

class MySystem(ServerSubsystem):
    canTick = True

    def onUpdate(self, dt):
        with profiler.record('MySystem.onUpdate'):
            self.heavy_computation()
            self.world_query()
            self.sync_state()

    def heavy_computation(self):
        with profiler.record('MySystem.heavy'):
            # ... 复杂的计算
            pass

    def world_query(self):
        with profiler.record('MySystem.query'):
            # ... 大量的实体查询
            pass
```

### 3.2 获取统计

```python
# 查看快照（不重置）
snap = profiler.snapshot()
for key, stats in snap.items():
    print('%s: avg=%.2fms max=%.2fms count=%d' %
          (key, stats['avg_ms'], stats['max_ms'], stats['count']))

# 获取统计并重置（适合周期性输出）
snap = profiler.flush()
```

### 3.3 控制记录

```python
# 临时禁用
profiler.disable()
do_non_critical_work()
profiler.enable()

# 只记录关键路径
with profiler.record('critical_path'):
    profiler.disable()
    do_auxiliary_work()
    profiler.enable()
    do_critical_work()
```

### 3.4 编程式记录

```python
import time

# 不使用 with，手动记录
start = time.time()
do_work()
elapsed = time.time() - start
profiler._add('manual_work', elapsed)
```

---

## 4. 框架自动记录

### 4.1 调度器跳过帧

框架在 `SubsystemManager.tickSubsystem()` 和 `tickRender()` 中自动记录：

```python
# 自动产生的 key：
profiler.flush()
# {
#     'scheduler.tickSkipped':   {'avg_ms': ..., 'max_ms': ..., 'count': ...},
#     'scheduler.renderSkipped': {'avg_ms': ..., 'max_ms': ..., 'count': ...},
# }
```

这些记录反映了调度器因重入保护跳过的帧数，用于诊断帧率波动。

### 4.2 子系统的诊断集成

可以在子系统中周期性输出 profiler 数据：

```python
class DiagnosticSystem(ServerSubsystem):
    canTick = True
    _report_interval = 300  # 每 300 tick 输出一次

    def onUpdate(self, dt):
        if self.ticks % self._report_interval == 0:
            snap = profiler.flush()
            if snap:
                print('=== Performance Report ===')
                sorted_keys = sorted(snap.items(),
                                    key=lambda x: x[1]['avg_ms'],
                                    reverse=True)
                for key, stats in sorted_keys[:10]:  # Top 10
                    print('  %-30s avg=%.2fms max=%.2fms count=%d' %
                          (key, stats['avg_ms'], stats['max_ms'], stats['count']))
```

---

## 5. `@TimeCost` 装饰器（遗留）

框架还提供了一个简单的 `@TimeCost` 装饰器，直接在控制台打印函数耗时：

```python
from architect.core.profiler import TimeCost

@TimeCost
def heavy_function():
    # ... 耗时操作
    pass

# 每次调用会输出：
# Time cost: 0.1234567890 s
```

**注意：** `@TimeCost` 是遗留 API，推荐使用 `profiler.record()` 获取更结构化的统计。

---

## 6. 最佳实践

1. **在关键路径上记录**：不用 `with` 包裹所有代码，只在性能敏感的操作上使用
   ```python
   # 好
   with profiler.record('ai.pathfinding'):
       self.find_path()

   # 不好（粒度太粗）
   with profiler.record('my_system'):
       self.do_everything()
   ```

2. **周期性输出统计**，而不是每帧都 `flush()`
3. **使用语义化的 key 名**，便于识别瓶颈
   ```python
   profiler.record('CombatSystem.damage_calc')  # 好
   profiler.record('func1')                      # 不好
   ```

4. **在生产环境中禁用** profiler 以节省开销：
   ```python
   profiler.disable()
   ```

5. **与日志结合**：在子系统初始化时检查 profiler 状态，按需启用：

   ```python
   def onInit(self):
       if DEBUG_MODE:
           profiler.enable()
       else:
           profiler.disable()
   ```

---

## 下一步

- [调度系统 (scheduler.md)](scheduler.md) — 了解调度器跳过帧机制
- [子系统 (subsystem.md)](subsystem.md) — 子系统生命周期
- [最佳实践 (best-practices.md)](best-practices.md) — 性能优化建议