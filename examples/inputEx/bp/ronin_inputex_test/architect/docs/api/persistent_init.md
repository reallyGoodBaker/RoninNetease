# 持久化数据 (Persistent) API

`architect.persistent` 模块提供了持久化数据存储功能，用于在游戏会话之间保存和加载数据。

## 模块结构

`architect.persistent` 模块包含以下子模块：

- `architect.persistent.client` - 客户端持久化数据
- `architect.persistent.common` - 通用持久化数据
- `architect.persistent.server` - 服务端持久化数据

## 概述

持久化数据模块用于存储需要在游戏会话之间保留的数据，例如：

- 玩家进度和成就
- 游戏设置和配置
- 世界状态和元数据
- 自定义游戏数据

## 设计原则

1. **分离关注点**: 客户端和服务端使用不同的持久化机制
2. **数据安全**: 服务端数据存储在服务器上，客户端数据存储在本地
3. **性能优化**: 使用缓存和批量操作提高性能
4. **错误处理**: 提供健壮的错误处理和恢复机制

## 使用模式

### 1. 客户端持久化

客户端持久化数据存储在玩家的本地设备上，适用于：

- 用户界面设置
- 客户端特定的配置
- 本地游戏进度
- 图形和音频设置

### 2. 服务端持久化

服务端持久化数据存储在服务器上，适用于：

- 玩家游戏数据
- 世界状态
- 多人游戏进度
- 服务器配置

### 3. 通用持久化

通用持久化提供跨客户端和服务端的统一接口，适用于：

- 数据同步
- 共享配置
- 跨平台数据

## 基本用法

### 客户端示例

```python
from ..architect.persistent.client import PersistentClient

# 创建持久化客户端
persistent = PersistentClient()

# 保存数据
persistent.set("player_settings", {
    "volume": 0.8,
    "difficulty": "normal",
    "controls": {"jump": "space", "sneak": "shift"}
})

# 加载数据
settings = persistent.get("player_settings")
if settings:
    volume = settings.get("volume", 0.5)
    print(f"音量设置: {volume}")

# 删除数据
persistent.remove("player_settings")
```

### 服务端示例

```python
from ..architect.persistent.server import PersistentServer

# 创建持久化服务端
persistent = PersistentServer()

# 保存玩家数据
def save_player_data(player_id, data):
    key = f"player_{player_id}"
    persistent.set(key, data)
    
# 加载玩家数据
def load_player_data(player_id):
    key = f"player_{player_id}"
    return persistent.get(key)

# 批量操作
def save_all_players(player_data_dict):
    persistent.batch_set(player_data_dict)
```

## 数据格式

持久化数据支持以下格式：

- **基本类型**: 字符串、整数、浮点数、布尔值
- **复合类型**: 列表、字典、元组
- **自定义对象**: 支持序列化的自定义类

### 序列化示例

```python
from ..architect.persistent.common import Serializable

class PlayerStats(Serializable):
    def __init__(self, level=1, experience=0, items=None):
        self.level = level
        self.experience = experience
        self.items = items or []
    
    def to_dict(self):
        return {
            "level": self.level,
            "experience": self.experience,
            "items": self.items
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            items=data.get("items", [])
        )

# 使用自定义对象
stats = PlayerStats(level=5, experience=1200, items=["sword", "shield"])
persistent.set("player_stats", stats.to_dict())

# 加载并恢复对象
data = persistent.get("player_stats")
if data:
    restored_stats = PlayerStats.from_dict(data)
```

## 高级功能

### 1. 数据版本控制

```python
from ..architect.persistent.common import VersionedData

class GameData(VersionedData):
    VERSION = "1.2.0"
    
    def __init__(self, content):
        super().__init__(content)
    
    def migrate(self, old_version, old_data):
        # 数据迁移逻辑
        if old_version == "1.0.0":
            # 从1.0.0迁移到1.2.0
            old_data["new_field"] = "default_value"
        elif old_version == "1.1.0":
            # 从1.1.0迁移到1.2.0
            old_data["renamed_field"] = old_data.pop("old_field_name")
        
        return old_data

# 使用版本控制
data = GameData({"score": 1000})
persistent.set("game_data", data)
```

### 2. 数据加密

```python
from ..architect.persistent.common import EncryptedStorage

# 创建加密存储
encrypted_storage = EncryptedStorage(
    encryption_key="your-secret-key",
    persistent_backend=persistent
)

# 加密保存
encrypted_storage.set_encrypted("sensitive_data", {
    "password_hash": "abc123",
    "email": "player@example.com"
})

# 解密加载
sensitive_data = encrypted_storage.get_decrypted("sensitive_data")
```

### 3. 数据缓存

```python
from ..architect.persistent.common import CachedPersistent

# 创建带缓存的持久化
cached_persistent = CachedPersistent(
    persistent_backend=persistent,
    cache_size=100,  # 缓存100个条目
    ttl=300  # 缓存有效期300秒
)

# 自动缓存的数据访问
for i in range(10):
    # 第一次访问从存储加载并缓存
    # 后续访问从缓存读取
    data = cached_persistent.get(f"item_{i}")
```

## 错误处理

```python
from ..architect.persistent.common import PersistentError

try:
    # 尝试保存数据
    persistent.set("important_data", large_data)
    
    # 验证数据
    if not persistent.exists("important_data"):
        raise PersistentError("数据保存失败")
    
    # 加载数据
    loaded_data = persistent.get("important_data")
    
except PersistentError as e:
    print(f"持久化错误: {e}")
    # 恢复或重试逻辑
    
except KeyError as e:
    print(f"键不存在: {e}")
    # 默认值处理
    
except Exception as e:
    print(f"未知错误: {e}")
    # 通用错误处理
```

## 性能优化

### 1. 批量操作

```python
# 批量保存（减少IO操作）
batch_data = {
    "player_1_stats": {"level": 5, "score": 1000},
    "player_2_stats": {"level": 3, "score": 500},
    "world_state": {"time": 1200, "weather": "sunny"}
}
persistent.batch_set(batch_data)

# 批量加载
keys = ["player_1_stats", "player_2_stats", "world_state"]
batch_results = persistent.batch_get(keys)
```

### 2. 延迟写入

```python
from ..architect.persistent.common import LazyPersistent

# 创建延迟写入的持久化
lazy_persistent = LazyPersistent(
    persistent_backend=persistent,
    flush_interval=60  # 每60秒刷新一次
)

# 多次写入只会在刷新时保存到磁盘
for i in range(100):
    lazy_persistent.set(f"temp_data_{i}", {"value": i})

# 手动刷新
lazy_persistent.flush()
```

### 3. 数据压缩

```python
from ..architect.persistent.common import CompressedPersistent

# 创建压缩存储
compressed_persistent = CompressedPersistent(
    persistent_backend=persistent,
    compression_level=6  # 压缩级别1-9
)

# 自动压缩的大型数据
large_data = {"array": list(range(1000000))}
compressed_persistent.set("large_array", large_data)
```

## 最佳实践

1. **键命名规范**: 使用有意义的键名，如 `player_{id}_stats`
2. **数据验证**: 保存前验证数据格式和完整性
3. **错误恢复**: 提供数据损坏时的恢复机制
4. **定期备份**: 重要数据定期备份到不同位置
5. **性能监控**: 监控持久化操作的性能和资源使用
6. **数据清理**: 定期清理过期或不再需要的数据
7. **并发安全**: 在多线程环境中确保数据一致性

## 注意事项

1. **存储限制**: 注意本地存储空间限制
2. **数据安全**: 敏感数据应加密存储
3. **版本兼容**: 考虑数据格式的向后兼容性
4. **性能影响**: 大量数据操作可能影响游戏性能
5. **平台差异**: 不同平台可能有不同的存储限制和特性
6. **网络延迟**: 服务端持久化可能受网络延迟影响
