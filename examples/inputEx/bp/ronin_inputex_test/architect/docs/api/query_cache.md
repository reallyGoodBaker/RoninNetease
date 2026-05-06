# 查询缓存 (Query Cache) API

`architect.query.cache` 模块提供了查询结果的缓存功能，用于提高查询性能。

## 类

### `QueryCache`

查询缓存类，用于缓存查询结果。

#### 构造函数

```python
def __init__(self, getter):
```

- **`getter`**: (函数) 获取数据的函数，无参数，返回要缓存的数据
- **初始化**: 立即调用 `getter` 函数并缓存结果

#### 属性

- `_getter`: 获取数据的函数
- `_cache`: 缓存的数据

#### 方法

##### `get()`

获取缓存的数据。

- **返回值**: 缓存的数据

##### `update()`

更新缓存的数据。

- **返回值**: 无

**注意**: 调用 `getter` 函数获取新数据并更新缓存。

## 函数

### `cache(getter, default=None)`

创建缓存装饰器。

- **`getter`**: (函数) 获取数据的函数
- **`default`**: (可选) 默认值，如果 `getter` 为 `None` 则使用此值
- **返回值**: 返回 `QueryCache(getter).get` 函数

## 使用示例

### 1. 基本缓存使用

```python
from ..architect.query.cache import QueryCache

# 创建数据获取函数
def get_player_count():
    """获取玩家数量（模拟耗时操作）"""
    import time
    time.sleep(0.1)  # 模拟耗时操作
    return len(get_all_players())  # 假设有这个函数

# 创建缓存
player_count_cache = QueryCache(get_player_count)

# 第一次获取（会调用 getter）
count1 = player_count_cache.get()  # 调用 get_player_count() 并缓存结果

# 第二次获取（使用缓存）
count2 = player_count_cache.get()  # 直接返回缓存结果，不调用 getter

# 更新缓存
player_count_cache.update()  # 重新调用 get_player_count() 更新缓存
count3 = player_count_cache.get()  # 获取更新后的结果
```

### 2. 使用缓存装饰器

```python
from ..architect.query.cache import cache

# 创建数据获取函数
def get_all_enemies():
    """获取所有敌人（模拟耗时操作）"""
    import time
    time.sleep(0.2)  # 模拟耗时操作
    return query(components=["EnemyComponent"]).execute()

# 创建缓存函数
cached_get_enemies = cache(get_all_enemies)

# 使用缓存函数
# 第一次调用会执行 get_all_enemies() 并缓存结果
enemies1 = cached_get_enemies()

# 后续调用直接返回缓存结果
enemies2 = cached_get_enemies()
enemies3 = cached_get_enemies()

# 如果需要更新缓存，需要重新创建缓存
fresh_cache = cache(get_all_enemies)
fresh_enemies = fresh_cache()
```

### 3. 游戏实体查询缓存

```python
from ..architect.query.cache import QueryCache
from ..architect.query import query

class EntityQueryCache:
    def __init__(self):
        self.caches = {}
    
    def get_entities_with_component(self, component_name):
        """获取具有指定组件的实体（带缓存）"""
        if component_name not in self.caches:
            # 创建缓存
            def getter():
                return query(components=[component_name]).execute()
            
            self.caches[component_name] = QueryCache(getter)
        
        return self.caches[component_name].get()
    
    def update_cache(self, component_name=None):
        """更新缓存"""
        if component_name:
            if component_name in self.caches:
                self.caches[component_name].update()
        else:
            # 更新所有缓存
            for cache in self.caches.values():
                cache.update()
    
    def clear_cache(self, component_name=None):
        """清除缓存"""
        if component_name:
            if component_name in self.caches:
                del self.caches[component_name]
        else:
            self.caches.clear()

# 使用示例
query_cache = EntityQueryCache()

# 获取玩家实体（带缓存）
players = query_cache.get_entities_with_component("PlayerComponent")

# 获取敌人实体（带缓存）
enemies = query_cache.get_entities_with_component("EnemyComponent")

# 更新玩家缓存
query_cache.update_cache("PlayerComponent")

# 清除所有缓存
query_cache.clear_cache()
```

### 4. 带过期时间的缓存

```python
import time
from ..architect.query.cache import QueryCache

class TimedQueryCache(QueryCache):
    def __init__(self, getter, ttl=1.0):
        """创建带过期时间的缓存"""
        super().__init__(getter)
        self.ttl = ttl  # 生存时间（秒）
        self.last_update = time.time()
    
    def get(self):
        """获取数据，如果过期则更新"""
        current_time = time.time()
        
        # 检查是否过期
        if current_time - self.last_update > self.ttl:
            self.update()
        
        return super().get()
    
    def update(self):
        """更新缓存并记录时间"""
        super().update()
        self.last_update = time.time()

# 使用示例
def get_game_state():
    """获取游戏状态（模拟耗时操作）"""
    import time
    time.sleep(0.1)
    return {
        "player_count": 10,
        "enemy_count": 25,
        "item_count": 50
    }

# 创建带过期时间的缓存（1秒过期）
game_state_cache = TimedQueryCache(get_game_state, ttl=1.0)

# 第一次获取
state1 = game_state_cache.get()  # 调用 get_game_state()

# 立即再次获取（使用缓存）
state2 = game_state_cache.get()  # 使用缓存

# 等待1.1秒后获取（缓存过期，重新获取）
time.sleep(1.1)
state3 = game_state_cache.get()  # 重新调用 get_game_state()
```

### 5. 条件缓存

```python
from ..architect.query.cache import QueryCache

class ConditionalQueryCache:
    def __init__(self):
        self.cache = None
        self.condition_met = False
    
    def get(self, getter, condition_checker):
        """根据条件获取数据"""
        if self.cache is None or not self.condition_met:
            # 条件不满足或缓存为空，获取新数据
            self.cache = getter()
            self.condition_met = condition_checker(self.cache)
        
        return self.cache
    
    def invalidate(self):
        """使缓存失效"""
        self.cache = None
        self.condition_met = False

# 使用示例
def get_dangerous_enemies():
    """获取危险敌人"""
    return query(
        components=["EnemyComponent"],
        filters=[lambda e, c: c["EnemyComponent"].danger_level > 5]
    ).execute()

def check_danger_condition(enemies):
    """检查危险条件：是否有危险敌人"""
    return len(enemies) > 0

cache_manager = ConditionalQueryCache()

# 获取危险敌人（只有当存在危险敌人才缓存）
enemies = cache_manager.get(get_dangerous_enemies, check_danger_condition)

# 如果 enemies 为空，下次调用会重新获取
# 如果 enemies 不为空，下次调用会使用缓存
```

## 缓存策略

### 1. 按需缓存

```python
class OnDemandCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key, getter):
        """按需获取数据"""
        if key not in self.cache:
            self.cache[key] = getter()
        return self.cache[key]
    
    def set(self, key, value):
        """设置缓存数据"""
        self.cache[key] = value
    
    def remove(self, key):
        """移除缓存数据"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """清除所有缓存"""
        self.cache.clear()

# 使用示例
cache = OnDemandCache()

# 按需缓存查询结果
def get_entities_by_type(entity_type):
    return cache.get(
        f"entities_{entity_type}",
        lambda: query(
            components=["EntityTypeComponent"],
            filters=[lambda e, c: c["EntityTypeComponent"].type == entity_type]
        ).execute()
    )

# 使用缓存
players = get_entities_by_type("player")
enemies = get_entities_by_type("enemy")
items = get_entities_by_type("item")
```

### 2. LRU缓存（最近最少使用）

```python
from collections import OrderedDict

class LRUQueryCache:
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key, getter):
        """获取数据，使用LRU策略"""
        if key in self.cache:
            # 移动到最近使用位置
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        
        # 缓存未命中，获取新数据
        value = getter()
        
        # 添加到缓存
        self.cache[key] = value
        
        # 检查缓存大小
        if len(self.cache) > self.max_size:
            # 移除最久未使用的项
            self.cache.popitem(last=False)
        
        return value
    
    def clear(self):
        """清除缓存"""
        self.cache.clear()

# 使用示例
lru_cache = LRUQueryCache(max_size=50)

def cached_query(components, filters=None):
    """带LRU缓存的查询"""
    # 创建缓存键
    key = f"query_{hash(str(components) + str(filters))}"
    
    return lru_cache.get(key, lambda: query(components=components, filters=filters).execute())

# 使用LRU缓存
for i in range(100):
    # 只有50个查询结果会被缓存
    results = cached_query([f"Component_{i % 20}"])
```

### 3. 写时更新缓存

```python
class WriteThroughCache:
    def __init__(self):
        self.cache = {}
        self.dirty = set()  # 脏数据集合
    
    def get(self, key, getter):
        """获取数据，如果脏则更新"""
        if key in self.dirty or key not in self.cache:
            # 数据脏或不存在，更新缓存
            self.cache[key] = getter()
            self.dirty.discard(key)
        
        return self.cache[key]
    
    def mark_dirty(self, key):
        """标记数据为脏"""
        self.dirty.add(key)
    
    def mark_all_dirty(self):
        """标记所有数据为脏"""
        self.dirty.update(self.cache.keys())

# 使用示例
cache = WriteThroughCache()

def get_player_inventory(player_id):
    """获取玩家库存"""
    return cache.get(
        f"inventory_{player_id}",
        lambda: query(
            components=["PlayerComponent", "InventoryComponent"],
            filters=[lambda e, c: c["PlayerComponent"].id == player_id]
        ).execute()
    )

# 当玩家库存发生变化时
def on_inventory_changed(player_id):
    # 标记缓存为脏
    cache.mark_dirty(f"inventory_{player_id}")
    
    # 下次获取时会重新查询
    inventory = get_player_inventory(player_id)
```

## 性能优化

### 1. 批量缓存更新

```python
class BatchCacheUpdater:
    def __init__(self, cache):
        self.cache = cache
        self.pending_updates = set()
    
    def schedule_update(self, key):
        """计划更新缓存"""
        self.pending_updates.add(key)
    
    def update_all(self):
        """批量更新所有计划的任务"""
        for key in self.pending_updates:
            if hasattr(self.cache, 'update'):
                self.cache.update()
            elif isinstance(self.cache, dict) and key in self.cache:
                # 假设缓存是字典，需要自定义更新逻辑
                pass
        
        self.pending_updates.clear()

# 使用示例
query_cache = QueryCache(lambda: query(components=["PositionComponent"]).execute())
updater = BatchCacheUpdater(query_cache)

# 游戏循环中
def game_loop():
    # 标记需要更新的缓存
    updater.schedule_update("position_query")
    updater.schedule_update("velocity_query")
    
    # 在合适的时机批量更新
    if frame_count % 10 == 0:  # 每10帧更新一次
        updater.update_all()
```

### 2. 缓存预热

```python
class CacheWarmer:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.warmup_queries = []
    
    def add_warmup_query(self, name, query_func):
        """添加预热查询"""
        self.warmup_queries.append((name, query_func))
    
    def warmup(self):
        """预热缓存"""
        print("开始预热缓存...")
        
        for name, query_func in self.warmup_queries:
            print(f"预热: {name}")
            # 执行查询以填充缓存
            result = query_func()
            self.cache_manager.set(name, result)
        
        print("缓存预热完成")

# 使用示例
cache_manager = OnDemandCache()
warmer = CacheWarmer(cache_manager)

# 添加预热查询
warmer.add_warmup_query(
    "all_players",
    lambda: query(components=["PlayerComponent"]).execute()
)

warmer.add_warmup_query(
    "all_enemies", 
    lambda: query(components=["EnemyComponent"]).execute()
)

warmer.add_warmup_query(
    "movable_entities",
    lambda: query(components=["PositionComponent", "VelocityComponent"]).execute()
)

# 游戏启动时预热缓存
warmer.warmup()
```

## 注意事项

1. **缓存一致性**: 确保缓存数据与真实数据一致
2. **内存使用**: 缓存可能占用大量内存，需要合理管理
3. **过期策略**: 需要合适的缓存过期机制
4. **并发访问**: 在多线程环境中需要线程安全
5. **错误处理**: 缓存失败时应有降级策略
6. **性能监控**: 监控缓存命中率和性能
7. **缓存穿透**: 防止频繁查询不存在的数据
8. **缓存雪崩**: 防止大量缓存同时失效

## 最佳实践

### 1. 监控缓存性能

```python
class MonitoredCache:
    def __init__(self, cache):
        self.cache = cache
        self.hits = 0
        self.misses = 0
    
    def get(self, key, getter):
        """获取数据并记录性能"""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            value = getter()
            self.cache[key] = value
            return value
    
    def hit_rate(self):
        """计算命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
    
    def stats(self):
        """获取统计信息"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate(),
            "size": len(self.cache)
        }
```

### 2. 分层缓存

```python
class LayeredCache:
    def __init__(self):
        self.l1_cache = {}  # 一级缓存（快速，容量小）
        self.l2_cache = {}  # 二级缓存（较慢，容量大）
    
    def get(self, key, getter):
        """从分层缓存获取数据"""
        # 尝试一级缓存
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # 尝试二级缓存
        if key in self.l2_cache:
            # 提升到一级缓存
            value = self.l2_cache[key]
            self.l1_cache[key] = value
            return value
        
        # 缓存未命中，获取新数据
        value = getter()
        
        # 同时存入两级缓存
        self.l1_cache[key] = value
        self.l2_cache[key] = value
        
        # 管理一级缓存大小
        if len(self.l1_cache) > 100:
            # 移除最旧的项（简单实现）
            oldest_key = next(iter(self.l1_cache))
            del self.l1_cache[oldest_key]
        
        return value
```

### 3. 缓存清理策略

```python
class SmartCache:
    def __init__(self, max_size=1000, cleanup_threshold=0.8):
        self.cache = {}
        self.access_count = {}
        self.max_size = max_size
        self.cleanup_threshold = cleanup_threshold
    
    def get(self, key, getter):
        """获取数据并记录访问次数"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        
        # 检查是否需要清理
        if len(self.cache) >= self.max_size * self.cleanup_threshold:
            self.cleanup()
        
        # 获取新数据
        value = getter()
        self.cache[key] = value
        self.access_count[key] = 1
        
        return value
    
    def cleanup(self):
        """清理不常用的缓存"""
        # 按访问次数排序
        sorted_items = sorted(
            self.access_count.items(),
            key=lambda x: x[1]
        )
        
        # 移除访问次数最少的一半
        remove_count = len(sorted_items) // 2
        for key, _ in sorted_items[:remove_count]:
            del self.cache[key]
            del self.access_count[key]
```
