# 客户端持久化数据 (Persistent Client) API

`architect.persistent.client` 模块提供了客户端键值数据库功能，用于在客户端存储和检索持久化数据。

## 类

### `ClientKVDatabase`

客户端键值数据库类，用于存储当前世界的持久化数据。

#### 继承

- `ClientSubsystem` - 客户端子系统基类
- `DBSource` - 数据库源接口

#### 装饰器

- `@SubsystemClient` - 客户端子系统装饰器

#### 构造函数

```python
def __init__(self, system, engine, sysName):
```

- **`system`**: 子系统管理器
- **`engine`**: 引擎实例
- **`sysName`**: 子系统名称

#### 属性

- `conf`: `LevelClient.getInstance().configClient` - 客户端配置管理器
- `data`: 从配置中加载的数据字典

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

**注意**: 设置数据后会立即保存到配置中。

##### `removeData(key)`

移除指定键的数据。

- **`key`**: (字符串) 数据键
- **返回值**: 无

**注意**: 如果键不存在会抛出 `KeyError`。

##### `clearData()`

清除所有数据。

- **返回值**: 无

#### 私有方法

##### `_save()`

保存数据到配置。

- **返回值**: 无

### `ClientKVDatabaseGlobal`

全局客户端键值数据库类，用于存储跨世界的持久化数据。

#### 继承

- `ClientSubsystem` - 客户端子系统基类
- `DBSource` - 数据库源接口

#### 装饰器

- `@SubsystemClient` - 客户端子系统装饰器

#### 构造函数

```python
def __init__(self, system, engine, sysName):
```

- **`system`**: 子系统管理器
- **`engine`**: 引擎实例
- **`sysName`**: 子系统名称

#### 属性

- `conf`: `LevelClient.getInstance().configClient` - 客户端配置管理器
- `data`: 从全局配置中加载的数据字典

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

**注意**: 设置数据后会立即保存到全局配置中。

##### `removeData(key)`

移除指定键的数据。

- **`key`**: (字符串) 数据键
- **返回值**: 无

**注意**: 如果键不存在会抛出 `KeyError`。

##### `clearData()`

清除所有数据。

- **返回值**: 无

#### 私有方法

##### `_save()`

保存数据到全局配置。

- **返回值**: 无

## 配置常量

### `DB_NAME`

- **类型**: 字符串
- **说明**: 当前世界数据库的配置名称

### `DB_GLOBAL_NAME`

- **类型**: 字符串
- **说明**: 全局数据库的配置名称

## 使用示例

### 1. 基本数据存储

```python
from ..architect.persistent.client import ClientKVDatabase

# 假设已通过子系统管理器获取实例
db = ClientKVDatabase(system, engine, "kv_database")

# 存储数据
db.setData("player_name", "Steve")
db.setData("player_level", 5)
db.setData("inventory", ["sword", "shield", "potion"])

# 读取数据
name = db.getData("player_name")  # "Steve"
level = db.getData("player_level")  # 5
inventory = db.getData("inventory")  # ["sword", "shield", "potion"]

# 删除数据
db.removeData("player_level")

# 检查删除
level = db.getData("player_level")  # None
```

### 2. 全局数据存储

```python
from ..architect.persistent.client import ClientKVDatabaseGlobal

# 假设已通过子系统管理器获取实例
global_db = ClientKVDatabaseGlobal(system, engine, "kv_database_global")

# 存储全局数据（跨世界保存）
global_db.setData("total_play_time", 3600)  # 秒
global_db.setData("achievements", ["first_kill", "diamond_finder"])
global_db.setData("settings", {"volume": 0.8, "language": "zh_CN"})

# 读取全局数据
play_time = global_db.getData("total_play_time")
achievements = global_db.getData("achievements")
settings = global_db.getData("settings")
```

### 3. 数据管理工具类

```python
class PlayerDataManager:
    def __init__(self, db, global_db):
        self.db = db  # 当前世界数据库
        self.global_db = global_db  # 全局数据库
    
    def save_player_progress(self, player_id, progress_data):
        """保存玩家进度"""
        key = f"player_{player_id}_progress"
        self.db.setData(key, progress_data)
    
    def load_player_progress(self, player_id):
        """加载玩家进度"""
        key = f"player_{player_id}_progress"
        return self.db.getData(key) or {}
    
    def save_player_settings(self, player_id, settings):
        """保存玩家设置（全局）"""
        key = f"player_{player_id}_settings"
        self.global_db.setData(key, settings)
    
    def load_player_settings(self, player_id):
        """加载玩家设置（全局）"""
        key = f"player_{player_id}_settings"
        return self.global_db.getData(key) or {}
    
    def clear_player_data(self, player_id):
        """清除玩家所有数据"""
        # 清除当前世界数据
        progress_key = f"player_{player_id}_progress"
        if progress_key in self.db.data:
            self.db.removeData(progress_key)
        
        # 清除全局数据
        settings_key = f"player_{player_id}_settings"
        if settings_key in self.global_db.data:
            self.global_db.removeData(settings_key)
```

### 4. 游戏设置管理

```python
class GameSettings:
    def __init__(self, global_db):
        self.db = global_db
        self.default_settings = {
            "graphics": {
                "quality": "medium",
                "render_distance": 8,
                "particles": True
            },
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.8,
                "sfx_volume": 0.9
            },
            "controls": {
                "sensitivity": 0.5,
                "invert_y": False
            }
        }
    
    def get_settings(self):
        """获取游戏设置"""
        settings = self.db.getData("game_settings")
        if not settings:
            # 使用默认设置
            settings = self.default_settings
            self.db.setData("game_settings", settings)
        return settings
    
    def update_settings(self, category, key, value):
        """更新游戏设置"""
        settings = self.get_settings()
        
        if category not in settings:
            settings[category] = {}
        
        settings[category][key] = value
        self.db.setData("game_settings", settings)
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        self.db.setData("game_settings", self.default_settings)
```

## 数据存储位置

### 当前世界数据库 (`ClientKVDatabase`)

- **存储位置**: 当前世界的配置文件中
- **数据范围**: 仅限当前世界
- **数据生命周期**: 世界卸载时数据可能丢失（取决于具体实现）
- **适用场景**: 世界特定的数据，如世界进度、临时设置

### 全局数据库 (`ClientKVDatabaseGlobal`)

- **存储位置**: 全局配置文件中
- **数据范围**: 跨所有世界
- **数据生命周期**: 持久保存，直到手动删除
- **适用场景**: 玩家设置、成就、统计数据

## 注意事项

1. **数据类型**: 支持 Python 基本数据类型（字符串、数字、列表、字典等）
2. **序列化**: 数据会自动序列化为 JSON 格式存储
3. **性能**: 每次写入都会保存到磁盘，频繁写入可能影响性能
4. **存储限制**: 受客户端配置文件大小限制
5. **数据安全**: 存储在本地，可能被用户修改
6. **错误处理**: 键不存在时 `getData` 返回 `None`，`removeData` 会抛出 `KeyError`
7. **并发访问**: 在单线程环境中使用，不需要考虑并发问题
8. **数据备份**: 重要数据应考虑备份机制

## 最佳实践

### 1. 键命名规范

```python
# 使用有意义的键名
# 格式: {entity}_{id}_{data_type}
db.setData("player_123_progress", {...})
db.setData("world_default_settings", {...})
db.setData("achievement_first_login", True)
```

### 2. 数据验证

```python
def save_validated_data(db, key, data):
    """保存验证后的数据"""
    if not isinstance(key, str):
        raise ValueError("键必须是字符串")
    
    if data is None:
        raise ValueError("数据不能为None")
    
    # 验证数据大小（示例）
    import json
    data_size = len(json.dumps(data))
    if data_size > 1024 * 1024:  # 1MB限制
        raise ValueError("数据大小超过限制")
    
    db.setData(key, data)
```

### 3. 数据迁移

```python
class DataMigrator:
    def __init__(self, db):
        self.db = db
    
    def migrate_player_data(self, old_key, new_key):
        """迁移玩家数据"""
        old_data = self.db.getData(old_key)
        if old_data:
            # 转换数据格式
            new_data = self.convert_format(old_data)
            self.db.setData(new_key, new_data)
            self.db.removeData(old_key)
    
    def convert_format(self, old_data):
        """转换数据格式"""
        # 实现具体的格式转换逻辑
        return {
            "version": "2.0",
            "data": old_data
        }
```

### 4. 批量操作

```python
def batch_save(db, data_dict):
    """批量保存数据"""
    for key, value in data_dict.items():
        db.setData(key, value)

def batch_load(db, keys):
    """批量加载数据"""
    result = {}
    for key in keys:
        result[key] = db.getData(key)
    return result
```

## 错误处理示例

```python
from ..architect.persistent.client import ClientKVDatabase

def safe_data_operation(db):
    try:
        # 尝试读取数据
        data = db.getData("important_data")
        
        if data is None:
            # 数据不存在，使用默认值
            data = {"default": True}
            db.setData("important_data", data)
        
        # 修改数据
        data["modified"] = True
        db.setData("important_data", data)
        
        # 删除测试数据
        db.removeData("test_data")
        
    except KeyError as e:
        print(f"键错误: {e}")
        # 处理键不存在的情况
        
    except Exception as e:
        print(f"未知错误: {e}")
        # 记录错误并恢复
        
    finally:
        # 清理资源（如果需要）
        pass
```
