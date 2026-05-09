# 通用查询 (Query Common) API

`architect.query.common` 模块提供了 ECS（实体-组件-系统）架构中的通用查询功能，包括查询装饰器和相关类型。

## 依赖

- `..component.getComponent` - 获取实体组件
- `..component.getComponentWithQuery` - 使用查询获取组件
- `..component.getEntities` - 获取所有实体

## 类

### `_Query`

内部查询类，用于表示一个查询对象。

#### 构造函数

```python
def __init__(self, entityId, comps):
```

- **`entityId`**: (字符串) 实体ID
- **`comps`**: (列表) 组件列表

#### 方法

##### `iter()`

迭代查询结果。

- **返回值**: 组件列表，如果不存在则返回空列表

##### `__enter__()`

上下文管理器入口。

- **返回值**: 查询结果
- **异常**: 如果查询结果为空则抛出异常

##### `__exit__(exc_type, exc_val, exc_tb)`

上下文管理器出口。

- **返回值**: `True`（抑制异常）

### `EntityId`

伪组件类，用于在查询中获取实体ID。

### `ExtraArguments`

伪组件类，用于在查询中获取额外参数列表。

### `ExtraArgDict`

伪组件类，用于在查询中获取额外参数字典。

## 函数

### `query(entityId, comps)`

创建查询对象。

- **`entityId`**: (整数) 实体ID
- **`comps`**: (列表) 组件列表
- **返回值**: `_Query` 实例

### `_getQueryArgs(entityId, compCls, required, excluded, args, kwargs)`

内部函数，获取查询参数。

- **`entityId`**: (字符串) 实体ID
- **`compCls`**: (列表) 组件类列表
- **`required`**: (列表) 必须包含的组件（不会包含在结果中）
- **`excluded`**: (列表) 必须排除的组件（不会包含在结果中）
- **`args`**: (列表) 额外参数列表
- **`kwargs`**: (字典) 额外参数字典
- **返回值**: 组件列表，如果查询失败则返回 `None`

### `Query(*compCls, **options)`

查询装饰器，用于装饰系统方法，使其能够查询具有特定组件的实体。

#### 参数

- **`*compCls`**: (可变参数) 组件类或组件类名列表
- **`required`**: (关键字参数) 必须包含的组件列表，不会包含在查询结果中
- **`excluded`**: (关键字参数) 必须排除的组件列表，不会包含在查询结果中

#### 返回值

装饰器函数

#### 使用说明

1. **必须搭配调度器使用**: 请一定要搭配 `Sched.Tick()`、`Sched.Render()` 等调度装饰器使用，否则不会执行。

2. **`self` 参数**: 使用 `Query` 查询时，`self` 为类实例，不再是实体ID字符串。组件可以自行缓存实体ID。

3. **伪组件**: 可以使用伪组件 `EntityId`、`ExtraArguments`、`ExtraArgDict` 来分别获取：
   - `EntityId`: 组件绑定的实体ID
   - `ExtraArguments`: 传入方法的参数列表
   - `ExtraArgDict`: 传入方法的参数字典

4. **参数注入**: 被这个装饰器装饰后，函数不会正常接收参数，而是在查询过程中动态注入参数。

5. **注意事项**: 请不要尝试在子系统类中使用 `self.xxx` 调用被这个装饰器装饰的方法，除非你非常了解动态参数注入是如何实现的。

6. **向后兼容性**: 无法支持此版本之前的代码，请重构代码以使用此版本。重构方法为导入伪组件 `EntityId`，在参数列表的 `self` 后面加入 `id,`，将之前代码中使用的 `self` 替换成 `id`。

## 使用示例

### 1. 基本查询

```python
from ..architect.query.common import Query
from ..architect.scheduler import Sched

class MovementSystem:
    @Sched.Tick()
    @Query("PositionComponent", "VelocityComponent")
    def update_position(self, position, velocity):
        """更新具有位置和速度组件的实体的位置"""
        position.x += velocity.dx
        position.y += velocity.dy
        position.z += velocity.dz
        
        # 记录更新
        print(f"更新实体位置: ({position.x}, {position.y}, {position.z})")
```

### 2. 使用伪组件

```python
from ..architect.query.common import Query, EntityId, ExtraArguments, ExtraArgDict
from ..architect.scheduler import Sched

class DamageSystem:
    @Sched.Tick()
    @Query("HealthComponent", EntityId, ExtraArguments, ExtraArgDict)
    def apply_damage(self, health, entity_id, args, kwargs):
        """应用伤害到实体"""
        # args 和 kwargs 来自调用时的参数
        damage_amount = args[0] if args else 0
        damage_type = kwargs.get('damage_type', 'physical')
        
        # 应用伤害
        health.current -= damage_amount
        
        # 记录伤害
        print(f"实体 {entity_id} 受到 {damage_amount} 点 {damage_type} 伤害")
        print(f"剩余生命值: {health.current}/{health.max}")
        
        # 检查死亡
        if health.current <= 0:
            self.kill_entity(entity_id)
    
    def kill_entity(self, entity_id):
        """杀死实体"""
        print(f"实体 {entity_id} 死亡")
```

### 3. 条件查询（required 和 excluded）

```python
from ..architect.query.common import Query
from ..architect.scheduler import Sched

class RenderSystem:
    @Sched.Render()
    @Query("RenderComponent", "PositionComponent", 
           required=["ActiveComponent"],  # 必须包含 ActiveComponent，但不会传递给方法
           excluded=["InvisibleComponent"])  # 不能包含 InvisibleComponent
    def render_entity(self, render, position):
        """渲染可见的活跃实体"""
        # 只有同时具有 ActiveComponent 且没有 InvisibleComponent 的实体会被渲染
        render.draw_at(position.x, position.y, position.z)
        
        # 更新渲染状态
        render.last_render_time = time.time()
```

### 4. 复杂查询系统

```python
from ..architect.query.common import Query, EntityId
from ..architect.scheduler import Sched
import time

class GameLogicSystem:
    def __init__(self):
        self.last_update_time = time.time()
    
    @Sched.Tick(interval=0.1)  # 每0.1秒执行一次
    @Query("PlayerComponent", "InventoryComponent", EntityId)
    def update_player_inventory(self, player, inventory, entity_id):
        """更新玩家库存"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        
        # 检查库存中的物品
        for item in inventory.items:
            if item.type == "food" and item.quantity > 0:
                # 自动消耗食物恢复饥饿值
                hunger_recovery = item.hunger_value * delta_time
                player.hunger = min(player.max_hunger, player.hunger + hunger_recovery)
                
                # 减少食物数量
                item.quantity -= delta_time * item.consumption_rate
                
                if item.quantity <= 0:
                    inventory.items.remove(item)
                    print(f"玩家 {player.name} 的食物 {item.name} 已耗尽")
        
        self.last_update_time = current_time
    
    @Sched.Tick(interval=1.0)  # 每1秒执行一次
    @Query("EnemyComponent", "AIComponent", EntityId)
    def update_enemy_ai(self, enemy, ai, entity_id):
        """更新敌人AI"""
        # 根据AI状态执行不同行为
        if ai.state == "patrol":
            self.patrol(enemy, ai)
        elif ai.state == "chase":
            self.chase(enemy, ai)
        elif ai.state == "attack":
            self.attack(enemy, ai)
        elif ai.state == "flee":
            self.flee(enemy, ai)
    
    def patrol(self, enemy, ai):
        """巡逻行为"""
        # 实现巡逻逻辑
        pass
    
    def chase(self, enemy, ai):
        """追逐行为"""
        # 实现追逐逻辑
        pass
    
    def attack(self, enemy, ai):
        """攻击行为"""
        # 实现攻击逻辑
        pass
    
    def flee(self, enemy, ai):
        """逃跑行为"""
        # 实现逃跑逻辑
        pass
```

### 5. 查询与事件系统结合

```python
from ..architect.query.common import Query, EntityId
from ..architect.scheduler import Sched
from ..architect.event import Event

class CombatSystem:
    def __init__(self):
        # 注册事件监听器
        Event.on("player_attacked", self.on_player_attacked)
        Event.on("enemy_spawned", self.on_enemy_spawned)
    
    @Sched.Tick()
    @Query("CombatComponent", "HealthComponent", EntityId)
    def update_combat(self, combat, health, entity_id):
        """更新战斗状态"""
        # 检查攻击冷却
        if combat.attack_cooldown > 0:
            combat.attack_cooldown -= 1
        
        # 检查自动攻击
        if combat.auto_attack and combat.attack_cooldown <= 0:
            self.perform_auto_attack(entity_id, combat)
    
    def on_player_attacked(self, attacker_id, target_id, damage):
        """玩家被攻击事件处理"""
        # 查找攻击者和目标
        attacker = self.get_entity(attacker_id)
        target = self.get_entity(target_id)
        
        if attacker and target:
            # 应用伤害
            self.apply_damage(attacker, target, damage)
            
            # 触发反击（如果有）
            if target.combat.auto_counter:
                self.counter_attack(target, attacker)
    
    def on_enemy_spawned(self, enemy_id, spawn_point):
        """敌人生成事件处理"""
        # 初始化敌人战斗组件
        enemy = self.get_entity(enemy_id)
        if enemy:
            enemy.combat = CombatComponent()
            enemy.combat.aggression_level = "high"
            enemy.combat.attack_range = 5.0
            
            print(f"敌人 {enemy_id} 在 {spawn_point} 生成，已初始化战斗组件")
    
    def perform_auto_attack(self, entity_id, combat):
        """执行自动攻击"""
        # 查找范围内的目标
        targets = self.find_targets_in_range(entity_id, combat.attack_range)
        
        for target_id in targets:
            # 计算伤害
            damage = combat.base_damage * combat.damage_multiplier
            
            # 触发攻击事件
            Event.emit("entity_attacked", entity_id, target_id, damage)
            
            # 重置冷却
            combat.attack_cooldown = combat.attack_speed
            
            print(f"实体 {entity_id} 自动攻击 {target_id}，造成 {damage} 点伤害")
            break  # 只攻击一个目标
    
    def find_targets_in_range(self, entity_id, range):
        """查找范围内的目标"""
        # 实现目标查找逻辑
        return []
```

### 6. 查询性能优化

```python
from ..architect.query.common import Query
from ..architect.scheduler import Sched
import time

class OptimizedSystem:
    def __init__(self):
        self.entity_cache = {}
        self.last_cache_update = 0
        self.cache_ttl = 5.0  # 缓存5秒
    
    @Sched.Tick()
    @Query("PositionComponent", "VelocityComponent")
    def update_movement(self, position, velocity):
        """优化后的移动更新"""
        current_time = time.time()
        
        # 检查缓存是否需要更新
        if current_time - self.last_cache_update > self.cache_ttl:
            self.update_entity_cache()
            self.last_cache_update = current_time
        
        # 使用缓存数据（如果有）
        cache_key = f"{position.entity_id}_{velocity.entity_id}"
        if cache_key in self.entity_cache:
            cached_data = self.entity_cache[cache_key]
            
            # 使用缓存数据加速计算
            position.x += cached_data.get("dx", 0)
            position.y += cached_data.get("dy", 0)
            position.z += cached_data.get("dz", 0)
        else:
            # 正常计算
            position.x += velocity.dx
            position.y += velocity.dy
            position.z += velocity.dz
    
    def update_entity_cache(self):
        """更新实体缓存"""
        # 清除旧缓存
        self.entity_cache.clear()
        
        # 这里可以预计算一些常用数据
        # 例如：计算所有实体的平均速度、位置范围等
        pass
    
    @Sched.Tick(interval=10.0)  # 每10秒执行一次
    @Query("PerformanceComponent")
    def monitor_performance(self, performance):
        """监控查询性能"""
        # 记录查询执行时间
        query_start = time.time()
        
        # 执行一些性能监控逻辑
        performance.query_count += 1
        performance.total_query_time += time.time() - query_start
        
        # 计算平均查询时间
        if performance.query_count > 0:
            performance.avg_query_time = performance.total_query_time / performance.query_count
        
        # 定期报告性能
        if performance.query_count % 100 == 0:
            print(f"查询性能统计:")
            print(f"  总查询次数: {performance.query_count}")
            print(f"  总查询时间: {performance.total_query_time:.4f}秒")
            print(f"  平均查询时间: {performance.avg_query_time:.6f}秒")
```

## 设计模式

### 1. 查询-处理模式

```python
class QueryProcessor:
    def __init__(self):
        self.queries = []
    
    def register_query(self, query_decorator, handler):
        """注册查询处理器"""
        self.queries.append((query_decorator, handler))
    
    def process_all(self):
        """处理所有注册的查询"""
        for query_decorator, handler in self.queries:
            # 执行查询并处理结果
            # 注意：这需要根据实际架构调整
            pass

# 使用示例
processor = QueryProcessor()

# 注册查询处理器
processor.register_query(
    Query("PlayerComponent", "HealthComponent"),
    lambda player, health: self.heal_player(player, health)
)

processor.register_query(
    Query("EnemyComponent", "AIComponent"),
    lambda enemy, ai: self.update_enemy_ai(enemy, ai)
)
```

### 2. 链式查询处理

```python
class QueryChain:
    def __init__(self):
        self.chain = []
    
    def add_step(self, query_decorator, processor):
        """添加查询处理步骤"""
        self.chain.append((query_decorator, processor))
    
    def execute(self):
        """执行查询链"""
        for query_decorator, processor in self.chain:
            # 执行查询并处理
            # 可以将上一步的结果传递给下一步
            pass

# 使用示例
chain = QueryChain()

# 构建处理链：查找敌人 -> 计算伤害 -> 应用伤害
chain.add_step(
    Query("EnemyComponent", "PositionComponent"),
    self.find_nearby_enemies
)

chain.add_step(
    Query("PlayerComponent", "WeaponComponent"),
    self.calculate_damage
)

chain.add_step(
    Query("HealthComponent"),
    self.apply_damage
)
```

## 注意事项

1. **调度器依赖**: `Query` 装饰器必须与调度器装饰器一起使用
2. **参数注入**: 被装饰的方法参数由查询动态注入，不是正常的方法参数
3. **性能考虑**: 复杂查询可能影响游戏性能
4. **实体生命周期**: 查询时实体可能已被销毁
5. **组件依赖**: 确保查询的组件已正确注册和初始化
6. **错误处理**: 查询失败时应适当处理异常
7. **缓存策略**: 频繁查询应考虑使用缓存
8. **并发安全**: 在多线程环境中需要确保查询安全
