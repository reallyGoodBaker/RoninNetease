# 客户端查询 (Query Client) API

`architect.query.queryClient` 模块提供了客户端专用的查询功能，包括实体组件查询和缓存管理。

## 依赖

- `..level.client.compClient` - 客户端组件管理器
- `..level.client.clientApi` - 客户端API
- `.cache.QueryCache` - 查询缓存类
- `.common.query` - 通用查询函数
- `.common.Query` - 查询装饰器

## 类

### `QueryClient`

客户端查询管理器类，提供实体组件查询和缓存功能。

#### 类属性

- `_caches`: 静态字典，存储所有查询缓存

#### 静态方法

##### `cache(key, id, getter)`

获取或创建查询缓存。

- **`key`**: (字符串) 缓存键
- **`id`**: (整数) 实体ID
- **`getter`**: (对象) 数据获取函数
- **返回值**: `QueryCache` 实例的 `get()` 方法返回值

**工作原理**:
1. 检查是否存在指定键的缓存字典
2. 如果不存在，创建新的 `QueryCache` 并存储
3. 如果存在，返回现有的缓存
4. 返回缓存数据的 `get()` 结果

##### `queryOfKey(key, entityFilter=None)`

获取指定键的所有缓存。

- **`key`**: (字符串) 缓存键
- **`entityFilter`**: (函数, 可选) 实体过滤器函数，接受实体ID返回布尔值
- **返回值**: 字典 `{实体ID: QueryCache}`

**过滤器函数签名**:
```python
def entityFilter(entity_id):
    # 返回 True 表示包含该实体，False 表示排除
    return entity_id % 2 == 0  # 示例：只返回偶数ID的实体
```

##### `queryOfEntity(entityId, keyFilter=None)`

获取指定实体的所有缓存。

- **`entityId`**: (整数) 实体ID
- **`keyFilter`**: (函数, 可选) 键过滤器函数，接受缓存键返回布尔值
- **返回值**: 字典 `{缓存键: QueryCache}`

**过滤器函数签名**:
```python
def keyFilter(cache_key):
    # 返回 True 表示包含该键，False 表示排除
    return cache_key.startswith("player_")  # 示例：只返回玩家相关的缓存
```

##### `pos(id)`

获取实体的位置组件。

- **`id`**: (整数) 实体ID
- **返回值**: 位置组件实例

##### `type(id)`

获取实体的类型组件。

- **`id`**: (整数) 实体ID
- **返回值**: 引擎类型组件实例

##### `rot(id)`

获取实体的旋转组件。

- **`id`**: (整数) 实体ID
- **返回值**: 旋转组件实例

##### `action(id)`

获取实体的动作组件。

- **`id`**: (整数) 实体ID
- **返回值**: 动作组件实例

##### `motion(id)`

获取实体的运动组件。

- **`id`**: (整数) 实体ID
- **返回值**: 演员运动组件实例

## 使用示例

### 1. 基本缓存使用

```python
from ..architect.query.queryClient import QueryClient

# 创建数据获取函数
def get_player_stats(player_id):
    """获取玩家统计数据（模拟耗时操作）"""
    import time
    time.sleep(0.05)  # 模拟网络延迟或计算耗时
    return {
        "level": 5,
        "experience": 1200,
        "health": 85,
        "mana": 60
    }

# 使用缓存获取玩家数据
player_id = 123
stats = QueryClient.cache("player_stats", player_id, lambda: get_player_stats(player_id))

print(f"玩家 {player_id} 的等级: {stats['level']}")
print(f"玩家 {player_id} 的经验: {stats['experience']}")

# 再次获取（使用缓存）
cached_stats = QueryClient.cache("player_stats", player_id, lambda: get_player_stats(player_id))
# 这次不会调用 get_player_stats，直接返回缓存结果
```

### 2. 查询实体组件

```python
from ..architect.query.queryClient import QueryClient

def update_entity_position(entity_id):
    """更新实体位置"""
    # 获取位置组件
    position = QueryClient.pos(entity_id)
    
    if position:
        # 更新位置
        position.x += 1.0
        position.y += 0.5
        position.z += 2.0
        
        print(f"实体 {entity_id} 位置更新: ({position.x}, {position.y}, {position.z})")
        return position
    else:
        print(f"实体 {entity_id} 没有位置组件")
        return None

def get_entity_type(entity_id):
    """获取实体类型"""
    entity_type = QueryClient.type(entity_id)
    
    if entity_type:
        print(f"实体 {entity_id} 类型: {entity_type.name}")
        return entity_type.name
    else:
        print(f"实体 {entity_id} 没有类型组件")
        return None

def rotate_entity(entity_id, yaw, pitch):
    """旋转实体"""
    rotation = QueryClient.rot(entity_id)
    
    if rotation:
        rotation.yaw = yaw
        rotation.pitch = pitch
        
        print(f"实体 {entity_id} 旋转: yaw={yaw}, pitch={pitch}")
        return rotation
    else:
        print(f"实体 {entity_id} 没有旋转组件")
        return None
```

### 3. 批量查询和过滤

```python
from ..architect.query.queryClient import QueryClient

def get_all_player_caches():
    """获取所有玩家的缓存"""
    # 获取所有"player_stats"键的缓存
    player_caches = QueryClient.queryOfKey("player_stats")
    
    print(f"找到 {len(player_caches)} 个玩家的缓存")
    
    for player_id, cache in player_caches.items():
        stats = cache.get()
        print(f"玩家 {player_id}: 等级={stats['level']}, 生命值={stats['health']}")
    
    return player_caches

def get_high_level_players(min_level=10):
    """获取高等级玩家的缓存"""
    def high_level_filter(player_id):
        # 获取玩家数据
        stats = QueryClient.cache("player_stats", player_id, lambda: {"level": 1})  # 默认值
        return stats.get("level", 0) >= min_level
    
    # 使用过滤器获取高等级玩家
    high_level_caches = QueryClient.queryOfKey("player_stats", high_level_filter)
    
    print(f"找到 {len(high_level_caches)} 个等级 >= {min_level} 的玩家")
    return high_level_caches

def get_entity_all_caches(entity_id):
    """获取实体的所有缓存"""
    entity_caches = QueryClient.queryOfEntity(entity_id)
    
    print(f"实体 {entity_id} 有 {len(entity_caches)} 个缓存:")
    for cache_key, cache in entity_caches.items():
        data = cache.get()
        print(f"  {cache_key}: {type(data).__name__}")
    
    return entity_caches

def get_player_specific_caches(entity_id):
    """获取实体的玩家相关缓存"""
    def player_key_filter(cache_key):
        return cache_key.startswith("player_")
    
    player_caches = QueryClient.queryOfEntity(entity_id, player_key_filter)
    
    print(f"实体 {entity_id} 有 {len(player_caches)} 个玩家相关缓存")
    return player_caches
```

### 4. 游戏实体管理系统

```python
from ..architect.query.queryClient import QueryClient
import time

class EntityManager:
    def __init__(self):
        self.last_update_time = time.time()
    
    def update_all_entities(self):
        """更新所有实体"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        
        # 获取所有实体的位置缓存
        position_caches = QueryClient.queryOfKey("entity_positions")
        
        for entity_id, cache in position_caches.items():
            self.update_entity_position(entity_id, cache, delta_time)
        
        # 获取所有实体的动作缓存
        action_caches = QueryClient.queryOfKey("entity_actions")
        
        for entity_id, cache in action_caches.items():
            self.update_entity_action(entity_id, cache, delta_time)
        
        self.last_update_time = current_time
    
    def update_entity_position(self, entity_id, position_cache, delta_time):
        """更新实体位置"""
        position_data = position_cache.get()
        
        # 获取运动组件
        motion = QueryClient.motion(entity_id)
        if not motion:
            return
        
        # 更新位置
        position_data["x"] += motion.velocity_x * delta_time
        position_data["y"] += motion.velocity_y * delta_time
        position_data["z"] += motion.velocity_z * delta_time
        
        # 更新缓存
        position_cache.update()
        
        # 同步到渲染
        self.sync_position_to_render(entity_id, position_data)
    
    def update_entity_action(self, entity_id, action_cache, delta_time):
        """更新实体动作"""
        action_data = action_cache.get()
        
        # 获取动作组件
        action = QueryClient.action(entity_id)
        if not action:
            return
        
        # 更新动作状态
        if action.is_moving:
            action_data["state"] = "moving"
            action_data["animation"] = "walk"
        elif action.is_attacking:
            action_data["state"] = "attacking"
            action_data["animation"] = "attack"
        else:
            action_data["state"] = "idle"
            action_data["animation"] = "idle"
        
        # 更新动作进度
        if action_data["state"] == "attacking":
            action_data["attack_progress"] += delta_time
            if action_data["attack_progress"] >= 1.0:
                action_data["attack_progress"] = 0.0
                action_data["can_attack_again"] = True
        
        # 更新缓存
        action_cache.update()
    
    def sync_position_to_render(self, entity_id, position_data):
        """同步位置到渲染系统"""
        # 获取位置组件并更新
        position = QueryClient.pos(entity_id)
        if position:
            position.x = position_data["x"]
            position.y = position_data["y"]
            position.z = position_data["z"]
    
    def create_entity_cache(self, entity_id, entity_type):
        """创建实体缓存"""
        # 创建位置缓存
        QueryClient.cache(
            "entity_positions",
            entity_id,
            lambda: {"x": 0, "y": 0, "z": 0, "last_updated": time.time()}
        )
        
        # 创建动作缓存
        QueryClient.cache(
            "entity_actions",
            entity_id,
            lambda: {"state": "idle", "animation": "idle", "attack_progress": 0.0}
        )
        
        # 根据实体类型创建特定缓存
        if entity_type == "player":
            QueryClient.cache(
                "player_stats",
                entity_id,
                lambda: {"level": 1, "experience": 0, "health": 100, "mana": 50}
            )
        elif entity_type == "enemy":
            QueryClient.cache(
                "enemy_stats",
                entity_id,
                lambda: {"health": 50, "damage": 10, "ai_state": "patrol"}
            )
        
        print(f"为实体 {entity_id} ({entity_type}) 创建了缓存")
    
    def remove_entity_cache(self, entity_id):
        """移除实体缓存"""
        # 获取实体的所有缓存键
        entity_caches = QueryClient.queryOfEntity(entity_id)
        
        # 从全局缓存中移除
        for cache_key in entity_caches.keys():
            if cache_key in QueryClient._caches:
                if entity_id in QueryClient._caches[cache_key]:
                    del QueryClient._caches[cache_key][entity_id]
        
        print(f"移除了实体 {entity_id} 的所有缓存")
```

### 5. 性能监控和优化

```python
from ..architect.query.queryClient import QueryClient
import time

class QueryPerformanceMonitor:
    def __init__(self):
        self.query_times = {}
        self.cache_hits = {}
        self.cache_misses = {}
    
    def monitor_cache_performance(self, key, entity_id, getter):
        """监控缓存性能"""
        start_time = time.time()
        
        # 检查缓存命中率
        cache_key = f"{key}_{entity_id}"
        if cache_key in self.cache_hits:
            self.cache_hits[cache_key] += 1
        else:
            self.cache_hits[cache_key] = 1
            self.cache_misses[cache_key] = 0
        
        # 执行查询
        result = QueryClient.cache(key, entity_id, getter)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # 记录查询时间
        if cache_key in self.query_times:
            self.query_times[cache_key].append(query_time)
        else:
            self.query_times[cache_key] = [query_time]
        
        return result
    
    def get_performance_stats(self):
        """获取性能统计"""
        stats = {}
        
        for cache_key in self.query_times.keys():
            times = self.query_times[cache_key]
            hits = self.cache_hits.get(cache_key, 0)
            misses = self.cache_misses.get(cache_key, 0)
            total_queries = hits + misses
            
            if total_queries > 0:
                hit_rate = hits / total_queries
                avg_time = sum(times) / len(times) if times else 0
                max_time = max(times) if times else 0
                min_time = min(times) if times else 0
                
                stats[cache_key] = {
                    "total_queries": total_queries,
                    "hit_rate": hit_rate,
                    "avg_time_ms": avg_time * 1000,
                    "max_time_ms": max_time * 1000,
                    "min_time_ms": min_time * 1000
                }
        
        return stats
    
    def print_performance_report(self):
        """打印性能报告"""
        stats = self.get_performance_stats()
        
        print("=== 查询性能报告 ===")
        for cache_key, data in stats.items():
            print(f"缓存键: {cache_key}")
            print(f"  总查询次数: {data['total_queries']}")
            print(f"  缓存命中率: {data['hit_rate']:.2%}")
            print(f"  平均查询时间: {data['avg_time_ms']:.2f}ms")
            print(f"  最大查询时间: {data['max_time_ms']:.2f}ms")
            print(f"  最小查询时间: {data['min_time_ms']:.2f}ms")
            print()

# 使用示例
monitor = QueryPerformanceMonitor()

def monitored_get_player_data(player_id):
    """被监控的玩家数据获取"""
    return monitor.monitor_cache_performance(
        "player_stats",
        player_id,
        lambda: {"level": 5, "experience": 1200}
    )

# 模拟多次查询
for i in range(100):
    data = monitored_get_player_data(123)
    time.sleep(0.01)  # 模拟间隔

# 打印性能报告
monitor.print_performance_report()
```

### 6. 缓存清理策略

```python
from ..architect.query.queryClient import QueryClient
import time

class CacheCleanupManager:
    def __init__(self, cleanup_interval=60.0, max_cache_age=300.0):
        self.cleanup_interval = cleanup_interval  # 清理间隔（秒）
        self.max_cache_age = max_cache_age  # 最大缓存年龄（秒）
        self.last_cleanup_time = time.time()
    
    def check_and_cleanup(self):
        """检查并执行缓存清理"""
        current_time = time.time()
        
        if current_time - self.last_cleanup_time >= self.cleanup_interval:
            self.cleanup_old_caches()
            self.last_cleanup_time = current_time
    
    def cleanup_old_caches(self):
        """清理旧缓存"""
        print("开始清理旧缓存...")
        
        cleaned_count = 0
        current_time = time.time()
        
        for cache_key, entity_cache in QueryClient._caches.items():
            entities_to_remove = []
            
            for entity_id, cache in entity_cache.items():
                # 检查缓存年龄（需要缓存对象支持年龄记录）
                if hasattr(cache, 'last_access_time'):
                    cache_age = current_time - cache.last_access_time
                    if cache_age > self.max_cache_age:
                        entities_to_remove.append(entity_id)
            
            # 移除过期缓存
            for entity_id in entities_to_remove:
                del entity_cache[entity_id]
                cleaned_count += 1
            
            # 如果缓存字典为空，移除整个键
            if not entity_cache:
                del QueryClient._caches[cache_key]
        
        print(f"清理完成，移除了 {cleaned_count} 个过期缓存")
    
    def force_cleanup_by_entity(self, entity_id):
        """强制清理指定实体的所有缓存"""
        if entity_id in QueryClient._caches.get("entity_positions", {}):
            del QueryClient._caches["entity_positions"][entity_id]
        
        if entity_id in QueryClient._caches.get("entity_actions", {}):
            del QueryClient._caches["entity_actions"][entity_id]
        
        if entity_id in QueryClient._caches.get("player_stats", {}):
            del QueryClient._caches["player_stats"][entity_id]
        
        print(f"强制清理了实体 {entity_id} 的所有缓存")
    
    def force_cleanup_by_key(self, cache_key):
        """强制清理指定键的所有缓存"""
        if cache_key in QueryClient._c