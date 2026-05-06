# 服务端持久化数据 (Persistent Server) API

`architect.persistent.server` 模块提供了服务端键值数据库功能，用于在服务端存储和检索持久化数据。

## 类

### `ServerKVDatabase`

服务端键值数据库类，用于存储服务端的持久化数据。

#### 继承

- `ServerSubsystem` - 服务端子系统基类
- `DBSource` - 数据库源接口

#### 装饰器

- `@SubsystemServer` - 服务端子系统装饰器

#### 类属性

- `data`: `LevelServer.extraData` - 服务端额外数据管理器

#### 构造函数

```python
def __init__(self, system, engine, sysName):
```

- **`system`**: 子系统管理器
- **`engine`**: 引擎实例
- **`sysName`**: 子系统名称

#### 方法

##### `getData(key)`

获取指定键的数据。

- **`key`**: (字符串) 数据键
- **返回值**: 键对应的值，如果键不存在则返回 `None`

##### `setData(key, value)`

设置指定键的数据。

- **`key`**: (字符串) 数据键
- **`value`**: 要存储的值
- **返回值**: 无

**注意**: 设置数据后会立即保存到额外数据中。

##### `removeData(key)`

移除指定键的数据。

- **`key`**: (字符串) 数据键
- **返回值**: 无

**实现**: 通过将键的值设置为 `None` 来移除数据。

##### `clearData()`

清除所有数据。

- **返回值**: 无

## 使用示例

### 1. 基本数据存储

```python
from ..architect.persistent.server import ServerKVDatabase

# 假设已通过子系统管理器获取实例
db = ServerKVDatabase(system, engine, "kv_database")

# 存储数据
db.setData("server_name", "My Minecraft Server")
db.setData("max_players", 20)
db.setData("game_mode", "survival")
db.setData("whitelist", ["player1", "player2", "player3"])

# 读取数据
server_name = db.getData("server_name")  # "My Minecraft Server"
max_players = db.getData("max_players")  # 20
game_mode = db.getData("game_mode")  # "survival"
whitelist = db.getData("whitelist")  # ["player1", "player2", "player3"]

# 删除数据
db.removeData("game_mode")

# 检查删除
game_mode = db.getData("game_mode")  # None
```

### 2. 玩家数据管理

```python
class PlayerDataManager:
    def __init__(self, db):
        self.db = db
    
    def save_player_data(self, player_id, data):
        """保存玩家数据"""
        key = f"player_{player_id}"
        self.db.setData(key, data)
    
    def load_player_data(self, player_id):
        """加载玩家数据"""
        key = f"player_{player_id}"
        return self.db.getData(key) or {}
    
    def update_player_stat(self, player_id, stat_name, value):
        """更新玩家统计"""
        key = f"player_{player_id}"
        player_data = self.load_player_data(player_id)
        
        if "stats" not in player_data:
            player_data["stats"] = {}
        
        player_data["stats"][stat_name] = value
        self.save_player_data(player_id, player_data)
    
    def get_all_player_ids(self):
        """获取所有玩家ID（需要自定义实现）"""
        # 注意：ServerKVDatabase 没有提供获取所有键的方法
        # 需要额外的机制来跟踪玩家ID
        return []

# 使用示例
db = ServerKVDatabase(system, engine, "player_db")
manager = PlayerDataManager(db)

# 保存玩家数据
manager.save_player_data("player_123", {
    "name": "Steve",
    "level": 5,
    "inventory": ["sword", "shield"],
    "stats": {"kills": 10, "deaths": 3}
})

# 更新玩家统计
manager.update_player_stat("player_123", "kills", 15)
```

### 3. 世界状态管理

```python
class WorldStateManager:
    def __init__(self, db):
        self.db = db
    
    def save_world_state(self, world_id, state_data):
        """保存世界状态"""
        key = f"world_{world_id}_state"
        self.db.setData(key, state_data)
    
    def load_world_state(self, world_id):
        """加载世界状态"""
        key = f"world_{world_id}_state"
        return self.db.getData(key) or {
            "time": 0,
            "weather": "clear",
            "spawn_point": (0, 64, 0),
            "structures": []
        }
    
    def update_world_time(self, world_id, time_value):
        """更新世界时间"""
        state = self.load_world_state(world_id)
        state["time"] = time_value
        self.save_world_state(world_id, state)
    
    def add_structure(self, world_id, structure_data):
        """添加世界结构"""
        state = self.load_world_state(world_id)
        if "structures" not in state:
            state["structures"] = []
        
        state["structures"].append(structure_data)
        self.save_world_state(world_id, state)

# 使用示例
db = ServerKVDatabase(system, engine, "world_db")
world_manager = WorldStateManager(db)

# 保存世界状态
world_manager.save_world_state("overworld", {
    "time": 6000,
    "weather": "rain",
    "spawn_point": (100, 64, 200),
    "structures": [
        {"type": "village", "position": (150, 64, 250)},
        {"type": "temple", "position": (-50, 64, 100)}
    ]
})

# 更新世界时间
world_manager.update_world_time("overworld", 12000)
```

### 4. 游戏进度管理

```python
class GameProgressManager:
    def __init__(self, db):
        self.db = db
    
    def save_quest_progress(self, quest_id, progress_data):
        """保存任务进度"""
        key = f"quest_{quest_id}_progress"
        self.db.setData(key, progress_data)
    
    def load_quest_progress(self, quest_id):
        """加载任务进度"""
        key = f"quest_{quest_id}_progress"
        return self.db.getData(key) or {
            "completed": False,
            "current_step": 0,
            "objectives": {}
        }
    
    def complete_quest(self, quest_id, player_id):
        """完成任务"""
        progress = self.load_quest_progress(quest_id)
        progress["completed"] = True
        progress["completed_by"] = player_id
        progress["completion_time"] = time.time()
        
        self.save_quest_progress(quest_id, progress)
        
        # 记录到全局进度
        self.record_quest_completion(player_id, quest_id)
    
    def record_quest_completion(self, player_id, quest_id):
        """记录任务完成情况"""
        key = f"player_{player_id}_completed_quests"
        completed_quests = self.db.getData(key) or []
        
        if quest_id not in completed_quests:
            completed_quests.append(quest_id)
            self.db.setData(key, completed_quests)

# 使用示例
db = ServerKVDatabase(system, engine, "progress_db")
progress_manager = GameProgressManager(db)

# 保存任务进度
progress_manager.save_quest_progress("find_treasure", {
    "completed": False,
    "current_step": 2,
    "objectives": {
        "find_map": True,
        "decipher_clues": True,
        "locate_treasure": False
    }
})

# 完成任务
progress_manager.complete_quest("find_treasure", "player_123")
```

## 数据存储位置

### 服务端额外数据 (`LevelServer.extraData`)

- **存储位置**: 服务端世界的额外数据存储中
- **数据范围**: 当前服务端世界
- **数据生命周期**: 世界卸载时数据可能丢失（取决于具体实现）
- **适用场景**: 世界状态、玩家数据、游戏进度

## 与客户端版本的差异

| 特性 | 服务端 (`ServerKVDatabase`) | 客户端 (`ClientKVDatabase`) |
|------|-----------------------------|-----------------------------|
| 环境 | 服务端 | 客户端 |
| 存储位置 | `LevelServer.extraData` | 客户端配置文件 |
| 数据范围 | 服务端世界 | 客户端本地 |
| 数据共享 | 所有客户端共享 | 仅当前客户端 |
| 数据安全 | 受服务器控制 | 可能被用户修改 |
| 性能影响 | 影响服务器性能 | 影响客户端性能 |
| 网络同步 | 需要手动同步到客户端 | 自动本地存储 |

## 注意事项

1. **数据类型**: 支持 Python 基本数据类型（字符串、数字、列表、字典等）
2. **序列化**: 数据会自动序列化为 Minecraft 支持的格式
3. **性能**: 每次写入都会保存到磁盘，频繁写入可能影响服务器性能
4. **存储限制**: 受服务器存储空间限制
5. **数据安全**: 存储在服务器上，相对安全
6. **错误处理**: 键不存在时 `getData` 返回 `None`
7. **并发访问**: 在多线程环境中使用，需要考虑并发问题
8. **数据备份**: 重要数据应考虑定期备份

## 最佳实践

### 1. 键命名规范

```python
# 使用有意义的键名
# 格式: {entity_type}_{id}_{data_type}
db.setData("player_123_stats", {...})
db.setData("world_overworld_state", {...})
db.setData("quest_find_treasure_progress", {...})
```

### 2. 数据版本控制

```python
class VersionedData:
    def __init__(self, db, key, version="1.0"):
        self.db = db
        self.key = key
        self.version = version
    
    def save(self, data):
        """保存带版本的数据"""
        versioned_data = {
            "version": self.version,
            "data": data,
            "timestamp": time.time()
        }
        self.db.setData(self.key, versioned_data)
    
    def load(self):
        """加载并检查版本"""
        versioned_data = self.db.getData(self.key)
        if not versioned_data:
            return None
        
        data_version = versioned_data.get("version", "1.0")
        if data_version != self.version:
            # 数据迁移
            migrated_data = self.migrate_data(data_version, versioned_data["data"])
            versioned_data["data"] = migrated_data
            versioned_data["version"] = self.version
            self.db.setData(self.key, versioned_data)
        
        return versioned_data["data"]
    
    def migrate_data(self, old_version, old_data):
        """迁移数据到新版本"""
        # 实现具体的迁移逻辑
        if old_version == "1.0":
            # 从1.0迁移到1.1
            old_data["new_field"] = "default"
        return old_data
```

### 3. 批量操作优化

```python
class BatchDatabase:
    def __init__(self, db, batch_size=10):
        self.db = db
        self.batch_size = batch_size
        self.pending_writes = {}
    
    def set_data(self, key, value):
        """批量设置数据"""
        self.pending_writes[key] = value
        
        if len(self.pending_writes) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """刷新所有待写入数据"""
        for key, value in self.pending_writes.items():
            self.db.setData(key, value)
        self.pending_writes.clear()
    
    def __del__(self):
        """析构时自动刷新"""
        if self.pending_writes:
            self.flush()

# 使用示例
db = ServerKVDatabase(system, engine, "kv_database")
batch_db = BatchDatabase(db, batch_size=5)

# 批量写入（每5次写入才保存一次）
for i in range(20):
    batch_db.set_data(f"item_{i}", {"value": i})

# 手动刷新剩余数据
batch_db.flush()
```

### 4. 数据验证

```python
def validate_server_data(key, value):
    """验证服务端数据"""
    # 检查键格式
    if not isinstance(key, str) or len(key) > 100:
        return False
    
    # 检查值大小（防止过大数据）
    import json
    try:
        json_size = len(json.dumps(value))
        if json_size > 1024 * 1024:  # 1MB限制
            return False
    except:
        return False
    
    # 检查值类型
    if value is None:
        return True
    
    valid_types = (str, int, float, bool, list, dict)
    if not isinstance(value, valid_types):
        return False
    
    # 递归检查嵌套结构
    def check_nested(obj, depth=0):
        if depth > 10:  # 防止无限递归
            return False
        
        if isinstance(obj, dict):
            for k, v in obj.items():
                if not isinstance(k, str):
                    return False
                if not check_nested(v, depth + 1):
                    return False
        elif isinstance(obj, list):
            for item in obj:
                if not check_nested(item, depth + 1):
                    return False
        
        return True
    
    return check_nested(value)

# 使用验证
def safe_set_data(db, key, value):
    if validate_server_data(key, value):
        db.setData(key, value)
    else:
        raise ValueError(f"无效的数据: key={key}, value={value}")
```

## 错误处理示例

```python
from ..architect.persistent.server import ServerKVDatabase

def safe_data_operation(db):
    try:
        # 尝试读取数据
        data = db.getData("important_server_data")
        
        if data is None:
            # 数据不存在，初始化默认值
            data = {
                "initialized": True,
                "created_at": time.time(),
                "version": "1.0"
            }
            db.setData("important_server_data", data)
        
        # 修改数据
        data["last_modified"] = time.time()
        data["modification_count"] = data.get("modification_count", 0) + 1
        
        # 保存修改
        db.setData("important_server_data", data)
        
        # 删除临时数据
        db.removeData("temp_data")
        
    except Exception as e:
        print(f"服务端数据操作错误: {e}")
        # 记录错误日志
        log_error(f"数据库错误: {e}")
        
        # 尝试恢复
        try:
            backup_data = db.getData("important_server_data_backup")
            if backup_data:
                db.setData("important_server_data", backup_data)
        except:
            pass  # 恢复失败
        
    finally:
        # 清理资源（如果需要）
        pass
```
