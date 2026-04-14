# 服务端查询 (Query Server) API

`architect.query.queryServer` 模块提供了服务端专用的查询功能，包括实体组件查询和缓存管理。

## 依赖

- `..level.server.compServer` - 服务端组件管理器
- `.cache.QueryCache` - 查询缓存类
- `.common.query` - 通用查询函数
- `.common.Query` - 查询装饰器

## 类

### `QueryServer`

服务端查询管理器类，提供实体组件查询和缓存功能。

#### 类属性

- `_caches`: 静态字典，存储所有查询缓存

#### 静态方法

##### `cache(key, id, getter)`

获取或创建查询缓存。

- **`key`**: (字符串) 缓存键
- **`id`**: (整数) 实体ID
- **`getter`**: (对象) 数据获取函数
- **返回值**: `QueryCache` 实例的 `get()` 方法返回值

**注意**: 此方法在文件中重复定义（第9-19行和第31-41行），实际使用时会使用后面的定义。

##### `queryOfKey(key, entityFilter=None)`

获取指定键的所有缓存。

- **`key`**: (字符串) 缓存键
- **`entityFilter`**: (函数, 可选) 实体过滤器函数，接受实体ID返回布尔值
- **返回值**: 字典 `{实体ID: QueryCache}`

**注意**: 代码中有拼写错误 `filter` 应为 `entityFilter`。

##### `pos(id)`

获取实体的位置组件（带缓存）。

- **`id`**: (整数) 实体ID
- **返回值**: 位置组件实例

**实现**: 使用缓存键 `'pos'` 缓存位置组件。

##### `action(id)`

获取实体的动作组件。

- **`id`**: (整数) 实体ID
- **返回值**: 动作组件实例

##### `dimension(id)`

获取实体的维度组件。

- **`id`**: (整数) 实体ID
- **返回值**: 维度组件实例

##### `definations(id)`

获取实体的定义组件。

- **`id`**: (整数) 实体ID
- **返回值**: 实体定义组件实例

**注意**: 方法名拼写错误，应为 `definitions`。

## 使用示例

### 1. 基本缓存使用

```python
from ..architect.query.queryServer import QueryServer

# 创建数据获取函数
def get_entity_data(entity_id):
    """获取实体数据（模拟耗时操作）"""
    import time
    time.sleep(0.1)  # 模拟数据库查询或计算耗时
    return {
        "name": f"Entity_{entity_id}",
        "type": "monster",
        "level": 10,
        "health": 100
    }

# 使用缓存获取实体数据
entity_id = 456
data = QueryServer.cache("entity_data", entity_id, lambda: get_entity_data(entity_id))

print(f"实体 {entity_id} 名称: {data['name']}")
print(f"实体 {entity_id} 类型: {data['type']}")
print(f"实体 {entity_id} 等级: {data['level']}")
print(f"实体 {entity_id} 生命值: {data['health']}")

# 再次获取（使用缓存）
cached_data = QueryServer.cache("entity_data", entity_id, lambda: get_entity_data(entity_id))
# 这次不会调用 get_entity_data，直接返回缓存结果
```

### 2. 查询实体组件

```python
from ..architect.query.queryServer import QueryServer

def update_server_entity_position(entity_id, new_x, new_y, new_z):
    """更新服务端实体位置"""
    # 获取位置组件（带缓存）
    position = QueryServer.pos(entity_id)
    
    if position:
        # 更新位置
        position.x = new_x
        position.y = new_y
        position.z = new_z
        
        print(f"服务端实体 {entity_id} 位置更新: ({position.x}, {position.y}, {position.z})")
        
        # 同步到客户端（需要其他机制）
        self.sync_position_to_clients(entity_id, position)
        
        return position
    else:
        print(f"服务端实体 {entity_id} 没有位置组件")
        return None

def get_entity_action(entity_id):
    """获取实体动作"""
    action = QueryServer.action(entity_id)
    
    if action:
        print(f"服务端实体 {entity_id} 动作: {action.name}")
        print(f"  是否移动: {action.is_moving}")
        print(f"  是否攻击: {action.is_attacking}")
        print(f"  动作状态: {action.state}")
        
        return action
    else:
        print(f"服务端实体 {entity_id} 没有动作组件")
        return None

def get_entity_dimension(entity_id):
    """获取实体维度"""
    dimension = QueryServer.dimension(entity_id)
    
    if dimension:
        print(f"服务端实体 {entity_id} 维度: {dimension.name}")
        print(f"  维度ID: {dimension.id}")
        print(f"  是否有效: {dimension.is_valid}")
        
        return dimension
    else:
        print(f"服务端实体 {entity_id} 没有维度组件")
        return None

def get_entity_definitions(entity_id):
    """获取实体定义"""
    definitions = QueryServer.definations(entity_id)  # 注意：拼写错误
    
    if definitions:
        print(f"服务端实体 {entity_id} 定义:")
        print(f"  实体类型: {definitions.entity_type}")
        print(f"  组件列表: {definitions.components}")
        print(f"  属性: {definitions.attributes}")
        
        return definitions
    else:
        print(f"服务端实体 {entity_id} 没有定义组件")
        return None
```

### 3. 批量查询和过滤

```python
from ..architect.query.queryServer import QueryServer

def get_all_entity_caches():
    """获取所有实体的缓存"""
    # 获取所有"entity_data"键的缓存
    entity_caches = QueryServer.queryOfKey("entity_data")
    
    print(f"找到 {len(entity_caches)} 个实体的缓存")
    
    for entity_id, cache in entity_caches.items():
        data = cache.get()
        print(f"实体 {entity_id}: 名称={data['name']}, 类型={data['type']}, 等级={data['level']}")
    
    return entity_caches

def get_monster_entities():
    """获取所有怪物实体的缓存"""
    def monster_filter(entity_id):
        # 获取实体数据
        data = QueryServer.cache("entity_data", entity_id, lambda: {"type": "unknown"})
        return data.get("type") == "monster"
    
    # 使用过滤器获取怪物实体
    monster_caches = QueryServer.queryOfKey("entity_data", monster_filter)
    
    print(f"找到 {len(monster_caches)} 个怪物实体")
    return monster_caches

def get_high_level_entities(min_level=5):
    """获取高等级实体的缓存"""
    def high_level_filter(entity_id):
        # 获取实体数据
        data = QueryServer.cache("entity_data", entity_id, lambda: {"level": 1})
        return data.get("level", 0) >= min_level
    
    # 使用过滤器获取高等级实体
    high_level_caches = QueryServer.queryOfKey("entity_data", high_level_filter)
    
    print(f"找到 {len(high_level_caches)} 个等级 >= {min_level} 的实体")
    return high_level_caches
```

### 4. 服务端实体管理系统

```python
from ..architect.query.queryServer import QueryServer
import time

class ServerEntityManager:
    def __init__(self):
        self.last_update_time = time.time()
        self.entity_count = 0
    
    def spawn_entity(self, entity_type, spawn_position):
        """生成实体"""
        entity_id = self.generate_entity_id()
        
        # 创建实体组件
        self.create_entity_components(entity_id, entity_type, spawn_position)
        
        # 创建实体缓存
        self.create_entity_cache(entity_id, entity_type)
        
        print(f"服务端生成实体 {entity_id} ({entity_type}) 在位置 {spawn_position}")
        self.entity_count += 1
        
        return entity_id
    
    def generate_entity_id(self):
        """生成实体ID"""
        # 简单的ID生成逻辑
        return int(time.time() * 1000) % 1000000
    
    def create_entity_components(self, entity_id, entity_type, position):
        """创建实体组件"""
        # 创建位置组件
        pos_component = QueryServer.pos(entity_id)
        if pos_component:
            pos_component.x = position[0]
            pos_component.y = position[1]
            pos_component.z = position[2]
        
        # 创建动作组件
        action_component = QueryServer.action(entity_id)
        if action_component:
            action_component.name = "idle"
            action_component.is_moving = False
            action_component.is_attacking = False
        
        # 根据实体类型设置其他组件
        if entity_type == "player":
            self.setup_player_components(entity_id)
        elif entity_type == "monster":
            self.setup_monster_components(entity_id)
        elif entity_type == "npc":
            self.setup_npc_components(entity_id)
    
    def create_entity_cache(self, entity_id, entity_type):
        """创建实体缓存"""
        # 创建实体数据缓存
        QueryServer.cache(
            "entity_data",
            entity_id,
            lambda: {
                "type": entity_type,
                "spawn_time": time.time(),
                "last_update": time.time(),
                "state": "active"
            }
        )
        
        # 创建位置缓存
        QueryServer.cache(
            "entity_positions",
            entity_id,
            lambda: {"x": 0, "y": 0, "z": 0, "last_sync": 0}
        )
        
        # 根据实体类型创建特定缓存
        if entity_type == "player":
            QueryServer.cache(
                "player_data",
                entity_id,
                lambda: {"name": f"Player_{entity_id}", "level": 1, "experience": 0}
            )
        elif entity_type == "monster":
            QueryServer.cache(
                "monster_data",
                entity_id,
                lambda: {"name": f"Monster_{entity_id}", "health": 100, "damage": 10}
            )
    
    def setup_player_components(self, entity_id):
        """设置玩家组件"""
        # 玩家特定的组件设置
        definitions = QueryServer.definations(entity_id)
        if definitions:
            definitions.entity_type = "player"
            definitions.components = ["Position", "Action", "Inventory", "Stats"]
    
    def setup_monster_components(self, entity_id):
        """设置怪物组件"""
        # 怪物特定的组件设置
        definitions = QueryServer.definations(entity_id)
        if definitions:
            definitions.entity_type = "monster"
            definitions.components = ["Position", "Action", "AI", "Combat"]
    
    def setup_npc_components(self, entity_id):
        """设置NPC组件"""
        # NPC特定的组件设置
        definitions = QueryServer.definations(entity_id)
        if definitions:
            definitions.entity_type = "npc"
            definitions.components = ["Position", "Action", "Dialogue", "Quest"]
    
    def update_all_entities(self):
        """更新所有实体"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        
        # 获取所有实体的数据缓存
        entity_caches = QueryServer.queryOfKey("entity_data")
        
        for entity_id, cache in entity_caches.items():
            self.update_entity(entity_id, cache, delta_time)
        
        self.last_update_time = current_time
    
    def update_entity(self, entity_id, data_cache, delta_time):
        """更新单个实体"""
        data = data_cache.get()
        
        # 更新实体状态
        data["last_update"] = time.time()
        
        # 根据实体类型执行不同的更新逻辑
        entity_type = data.get("type", "unknown")
        
        if entity_type == "player":
            self.update_player(entity_id, data, delta_time)
        elif entity_type == "monster":
            self.update_monster(entity_id, data, delta_time)
        elif entity_type == "npc":
            self.update_npc(entity_id, data, delta_time)
        
        # 更新缓存
        data_cache.update()
    
    def update_player(self, entity_id, data, delta_time):
        """更新玩家"""
        # 玩家特定的更新逻辑
        player_data = QueryServer.cache("player_data", entity_id, lambda: {})
        
        # 检查玩家是否在线
        if self.is_player_online(entity_id):
            # 更新玩家状态
            player_data["last_active"] = time.time()
            
            # 同步位置到客户端
            self.sync_player_position(entity_id)
    
    def update_monster(self, entity_id, data, delta_time):
        """更新怪物"""
        # 怪物特定的更新逻辑
        monster_data = QueryServer.cache("monster_data", entity_id, lambda: {})
        
        # 执行AI逻辑
        self.update_monster_ai(entity_id, monster_data, delta_time)
        
        # 检查战斗状态
        if monster_data.get("in_combat", False):
            self.update_monster_combat(entity_id, monster_data, delta_time)
    
    def update_npc(self, entity_id, data, delta_time):
        """更新NPC"""
        # NPC特定的更新逻辑
        # 例如：检查是否有玩家在附近需要对话
        nearby_players = self.get_nearby_players(entity_id, 10.0)  # 10米范围内
        
        if nearby_players:
            # 有玩家在附近，更新NPC状态
            data["has_nearby_players"] = True
            data["nearby_player_count"] = len(nearby_players)
        else:
            data["has_nearby_players"] = False
            data["nearby_player_count"] = 0
    
    def is_player_online(self, entity_id):
        """检查玩家是否在线"""
        # 简单的在线检查逻辑
        player_data = QueryServer.cache("player_data", entity_id, lambda: {})
        last_active = player_data.get("last_active", 0)
        
        # 如果5分钟内没有活动，认为离线
        return time.time() - last_active < 300
    
    def sync_player_position(self, entity_id):
        """同步玩家位置到客户端"""
        # 获取位置组件
        position = QueryServer.pos(entity_id)
        
        if position:
            # 获取位置缓存
            pos_cache = QueryServer.cache("entity_positions", entity_id, lambda: {})
            pos_data = pos_cache.get()
            
            # 检查是否需要同步
            current_time = time.time()
            if current_time - pos_data.get("last_sync", 0) > 1.0:  # 每秒同步一次
                # 更新缓存
                pos_data["x"] = position.x
                pos_data["y"] = position.y
                pos_data["z"] = position.z
                pos_data["last_sync"] = current_time
                
                # 同步到客户端（需要网络通信）
                self.send_position_update(entity_id, position)
                
                # 更新缓存
                pos_cache.update()
    
    def update_monster_ai(self, entity_id, monster_data, delta_time):
        """更新怪物AI"""
        # 获取动作组件
        action = QueryServer.action(entity_id)
        if not action:
            return
        
        # 简单的AI逻辑
        ai_state = monster_data.get("ai_state", "idle")
        
        if ai_state == "idle":
            # 空闲状态：随机移动或保持静止
            if random.random() < 0.1:  # 10%概率开始移动
                monster_data["ai_state"] = "patrol"
                action.is_moving = True
                action.name = "walk"
        elif ai_state == "patrol":
            # 巡逻状态：移动到随机位置
            if random.random() < 0.05:  # 5%概率停止巡逻
                monster_data["ai_state"] = "idle"
                action.is_moving = False
                action.name = "idle"
        
        # 更新动作组件
        if action.is_moving:
            # 更新位置（简单移动）
            position = QueryServer.pos(entity_id)
            if position:
                position.x += random.uniform(-1, 1) * delta_time
                position.z += random.uniform(-1, 1) * delta_time
    
    def update_monster_combat(self, entity_id, monster_data, delta_time):
        """更新怪物战斗"""
        # 获取动作组件
        action = QueryServer.action(entity_id)
        if not action:
            return
        
        # 检查攻击冷却
        attack_cooldown = monster_data.get("attack_cooldown", 0)
        
        if attack_cooldown <= 0:
            # 可以攻击
            target_id = monster_data.get("target_id")
            if target_id:
                # 执行攻击
                action.is_attacking = True
                action.name = "attack"
                
                # 应用伤害
                damage = monster_data.get("damage", 10)
                self.apply_damage(entity_id, target_id, damage)
                
                # 重置冷却
                monster_data["attack_cooldown"] = 2.0  # 2秒冷却
        else:
            # 冷却中
            monster_data["attack_cooldown"] = max(0, attack_cooldown - delta_time)
            
            if attack_cooldown <= 0:
                action.is_attacking = False
    
    def get_nearby_players(self, entity_id, radius):
        """获取附近的玩家"""
        # 获取当前实体的位置
        position = QueryServer.pos(entity_id)
        if not position:
            return []
        
        nearby_players = []
        
        # 获取所有玩家缓存
        player_caches = QueryServer.queryOfKey("player_data