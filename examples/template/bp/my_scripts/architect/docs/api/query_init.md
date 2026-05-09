# 查询系统 (Query) API

`architect.query` 模块提供了实体查询功能，用于在 ECS（实体-组件-系统）架构中查找和筛选实体。

## 模块结构

`architect.query` 模块包含以下子模块：

- `architect.query.common` - 通用查询接口和类型
- `architect.query.cache` - 查询缓存
- `architect.query.queryClient` - 客户端查询
- `architect.query.queryServer` - 服务端查询

## 导入的符号

从 `architect.query.common` 模块导入以下符号：

### `query`

查询函数，用于创建和执行查询。

### `Query`

查询类，表示一个查询对象。

### `EntityId`

实体ID类型，用于标识实体。

### `ExtraArgDict`

额外参数字典类型。

### `ExtraArguments`

额外参数类型。

## 使用示例

### 基本导入

```python
from ..architect.query import query, Query, EntityId, ExtraArgDict, ExtraArguments

# 创建查询
q = query(components=["Position", "Velocity"])

# 执行查询
results = q.execute()

# 处理结果
for entity_id, components in results:
    position = components["Position"]
    velocity = components["Velocity"]
    # 处理实体
```

### 查询实体

```python
from ..architect.query import query

# 查询具有特定组件的实体
def find_players_with_weapons():
    """查找所有携带武器的玩家"""
    q = query(
        components=["PlayerComponent", "InventoryComponent"],
        filters=[
            lambda entity, comps: "weapon" in comps["InventoryComponent"].items
        ]
    )
    
    results = q.execute()
    return [(entity_id, comps["PlayerComponent"]) for entity_id, comps in results]

# 查询特定位置的实体
def find_entities_near_position(position, radius):
    """查找指定位置附近的实体"""
    q = query(
        components=["PositionComponent"],
        filters=[
            lambda entity, comps: 
                distance(comps["PositionComponent"].position, position) <= radius
        ]
    )
    
    return q.execute()
```

### 使用查询缓存

```python
from ..architect.query import query
from ..architect.query.cache import QueryCache

# 创建带缓存的查询
cache = QueryCache()

def get_all_enemies():
    """获取所有敌人（使用缓存）"""
    q = query(components=["EnemyComponent"])
    
    # 使用缓存执行查询
    results = cache.execute(q)
    
    # 或者手动管理缓存
    if not cache.has(q):
        results = q.execute()
        cache.set(q, results)
    else:
        results = cache.get(q)
    
    return results
```

## 查询系统概述

### 设计目标

1. **性能**: 高效查询大量实体
2. **灵活性**: 支持复杂的查询条件
3. **缓存**: 提供查询结果缓存
4. **类型安全**: 提供类型提示和验证
5. **跨平台**: 支持客户端和服务端

### 核心概念

1. **实体 (Entity)**: 游戏中的对象，由唯一ID标识
2. **组件 (Component)**: 实体的数据部分
3. **查询 (Query)**: 用于查找具有特定组件的实体
4. **过滤器 (Filter)**: 用于进一步筛选查询结果
5. **缓存 (Cache)**: 存储查询结果以提高性能

## 查询模式

### 1. 组件查询

查找具有特定组件的所有实体。

```python
# 查找所有具有生命值的实体
health_entities = query(components=["HealthComponent"]).execute()

# 查找所有可移动的实体
movable_entities = query(components=["PositionComponent", "VelocityComponent"]).execute()
```

### 2. 条件查询

使用过滤器进行条件查询。

```python
# 查找生命值低于50%的实体
low_health_entities = query(
    components=["HealthComponent"],
    filters=[
        lambda entity, comps: comps["HealthComponent"].current < comps["HealthComponent"].max * 0.5
    ]
).execute()

# 查找特定类型的敌人
zombie_enemies = query(
    components=["EnemyComponent"],
    filters=[
        lambda entity, comps: comps["EnemyComponent"].type == "zombie"
    ]
).execute()
```

### 3. 组合查询

组合多个查询条件。

```python
# 查找所有携带武器且生命值大于0的玩家
armed_players = query(
    components=["PlayerComponent", "InventoryComponent", "HealthComponent"],
    filters=[
        lambda entity, comps: "weapon" in comps["InventoryComponent"].items,
        lambda entity, comps: comps["HealthComponent"].current > 0
    ]
).execute()
```

### 4. 空间查询

基于空间位置的查询。

```python
from ..architect.math.vec3 import vec, modulo

def find_entities_in_radius(center, radius):
    """查找指定半径内的实体"""
    q = query(
        components=["PositionComponent"],
        filters=[
            lambda entity, comps: 
                modulo(vec(comps["PositionComponent"].position) - vec(center)) <= radius
        ]
    )
    return q.execute()
```

## 性能优化

### 1. 查询缓存

```python
from ..architect.query.cache import QueryCache

class EntityManager:
    def __init__(self):
        self.query_cache = QueryCache()
    
    def get_visible_entities(self, camera_position, view_distance):
        """获取可见实体（使用缓存）"""
        q = query(
            components=["PositionComponent", "RenderComponent"],
            filters=[
                lambda entity, comps: 
                    distance(comps["PositionComponent"].position, camera_position) <= view_distance
            ]
        )
        
        # 使用缓存
        cache_key = f"visible_{camera_position}_{view_distance}"
        if not self.query_cache.has(cache_key):
            results = q.execute()
            self.query_cache.set(cache_key, results, ttl=1.0)  # 缓存1秒
        else:
            results = self.query_cache.get(cache_key)
        
        return results
```

### 2. 批量查询

```python
def batch_query_entities(queries):
    """批量执行多个查询"""
    results = {}
    for name, q in queries.items():
        results[name] = q.execute()
    return results

# 使用示例
queries = {
    "players": query(components=["PlayerComponent"]),
    "enemies": query(components=["EnemyComponent"]),
    "items": query(components=["ItemComponent"])
}

all_results = batch_query_entities(queries)
```

### 3. 增量查询

```python
class IncrementalQuery:
    def __init__(self, base_query):
        self.base_query = base_query
        self.last_results = None
    
    def get_changes(self):
        """获取自上次查询以来的变化"""
        current_results = self.base_query.execute()
        
        if self.last_results is None:
            changes = {
                "added": list(current_results.keys()),
                "removed": [],
                "updated": []
            }
        else:
            # 比较两次查询结果
            current_ids = set(current_results.keys())
            last_ids = set(self.last_results.keys())
            
            changes = {
                "added": list(current_ids - last_ids),
                "removed": list(last_ids - current_ids),
                "updated": []
            }
            
            # 检查更新的实体（需要自定义逻辑）
            for entity_id in current_ids & last_ids:
                if self.has_changed(entity_id, current_results[entity_id], self.last_results[entity_id]):
                    changes["updated"].append(entity_id)
        
        self.last_results = current_results
        return changes
    
    def has_changed(self, entity_id, current_data, last_data):
        """检查实体是否发生变化"""
        # 实现具体的变更检测逻辑
        return current_data != last_data
```

## 高级用法

### 1. 查询链

```python
class QueryChain:
    def __init__(self):
        self.queries = []
    
    def add(self, query_obj):
        """添加查询到链中"""
        self.queries.append(query_obj)
        return self
    
    def execute(self):
        """执行查询链"""
        results = None
        
        for q in self.queries:
            if results is None:
                results = set(q.execute().keys())
            else:
                results = results.intersection(set(q.execute().keys()))
        
        return list(results)

# 使用示例
chain = QueryChain()
chain.add(query(components=["PlayerComponent"]))
chain.add(query(components=["InventoryComponent"]))
chain.add(query(
    components=["HealthComponent"],
    filters=[lambda e, c: c["HealthComponent"].current > 0]
))

# 执行链式查询：查找所有携带物品且生命值大于0的玩家
player_ids = chain.execute()
```

### 2. 查询构建器

```python
class QueryBuilder:
    def __init__(self):
        self.components = []
        self.filters = []
    
    def with_component(self, component_name):
        """添加组件条件"""
        self.components.append(component_name)
        return self
    
    def with_filter(self, filter_func):
        """添加过滤器"""
        self.filters.append(filter_func)
        return self
    
    def build(self):
        """构建查询"""
        return query(components=self.components, filters=self.filters)
    
    def execute(self):
        """构建并执行查询"""
        return self.build().execute()

# 使用示例
results = (QueryBuilder()
    .with_component("PlayerComponent")
    .with_component("InventoryComponent")
    .with_filter(lambda e, c: len(c["InventoryComponent"].items) > 0)
    .execute())
```

### 3. 查询监控

```python
class QueryMonitor:
    def __init__(self, query_obj, name="unnamed"):
        self.query = query_obj
        self.name = name
        self.execution_count = 0
        self.total_time = 0
    
    def execute(self):
        """执行查询并记录性能"""
        import time
        
        start_time = time.time()
        results = self.query.execute()
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.execution_count += 1
        self.total_time += execution_time
        
        print(f"查询 '{self.name}' 执行时间: {execution_time:.4f}秒, "
              f"结果数量: {len(results)}, "
              f"平均时间: {self.total_time/self.execution_count:.4f}秒")
        
        return results

# 使用示例
monitored_query = QueryMonitor(
    query(components=["PositionComponent", "VelocityComponent"]),
    name="移动实体查询"
)

# 定期执行并监控
for _ in range(10):
    entities = monitored_query.execute()
    # 处理实体...
```

## 错误处理

```python
from ..architect.query import query

def safe_query_execution(q):
    """安全的查询执行"""
    try:
        results = q.execute()
        return results
    except KeyError as e:
        print(f"组件不存在: {e}")
        return []
    except Exception as e:
        print(f"查询执行错误: {e}")
        # 记录错误日志
        log_error(f"查询错误: {e}")
        return []

# 使用示例
q = query(components=["PositionComponent", "NonExistentComponent"])
results = safe_query_execution(q)  # 返回空列表而不是崩溃
```

## 最佳实践

### 1. 查询复用

```python
# 预定义常用查询
COMMON_QUERIES = {
    "all_players": query(components=["PlayerComponent"]),
    "all_enemies": query(components=["EnemyComponent"]),
    "movable_entities": query(components=["PositionComponent", "VelocityComponent"]),
    "renderable_entities": query(components=["PositionComponent", "RenderComponent"])
}

# 复用查询
def update_game_state():
    players = COMMON_QUERIES["all_players"].execute()
    enemies = COMMON_QUERIES["all_enemies"].execute()
    # ...
```

### 2. 查询优化

```python
# 避免在循环中创建查询
def process_entities_inefficient():
    """低效的实现"""
    for _ in range(100):
        # 每次循环都创建新查询
        q = query(components=["PositionComponent"])
        results = q.execute()
        # ...

def process_entities_efficient():
    """高效的实现"""
    # 预先创建查询
    q = query(components=["PositionComponent"])
    
    for _ in range(100):
        # 复用查询
        results = q.execute()
        # ...
```

### 3. 内存管理

```python
class QueryManager:
    def __init__(self, max_cache_size=100):
        self.queries = {}
        self.cache = {}
        self.max_cache_size = max_cache_size
    
    def register_query(self, name, query_obj):
        """注册查询"""
        self.queries[name] = query_obj
    
    def execute_query(self, name, use_cache=True):
        """执行查询（可选使用缓存）"""
        if name not in self.queries:
            raise ValueError(f"查询未注册: {name}")
        
        q = self.queries[name]
        
        if use_cache and name in self.cache:
            return self.cache[name]
        
        results = q.execute()
        
        if use_cache:
            # 管理缓存大小
            if len(self.cache) >= self.max_cache_size:
                # 移除最旧的缓存项
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[name] = results
        
        return results
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
```

## 注意事项

1. **性能影响**: 复杂查询可能影响游戏性能
2. **内存使用**: 查询结果缓存占用内存
3. **数据一致性**: 查询结果可能不是实时最新的
4. **线程安全**: 在多线程环境中需要同步
5. **错误处理**: 组件不存在时可能抛出异常
6. **查询复杂度**: 避免过于复杂的查询条件
7. **缓存失效**: 需要合理设置缓存过期时间
8. **资源清理**: 及时清理不再使用的查询和缓存
