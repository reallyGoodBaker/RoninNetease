# 通用持久化数据 (Persistent Common) API

`architect.persistent.common` 模块提供了持久化数据的通用接口和视图类，用于简化数据访问和操作。

## 类

### `DBSource`

数据库源抽象基类，定义了持久化数据存储的基本接口。

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

##### `removeData(key)`

移除指定键的数据。

- **`key`**: (字符串) 数据键
- **返回值**: 无

##### `clearData()`

清除所有数据。

- **返回值**: 无

##### `createView(key)`

创建字典视图。

- **`key`**: (字符串) 数据键
- **返回值**: `DatabaseView` 实例

##### `createArrayView(key)`

创建数组视图。

- **`key`**: (字符串) 数据键
- **返回值**: `DatabaseArrayView` 实例

### `DatabaseView`

字典视图类，提供对字典类型数据的便捷访问和操作。

#### 构造函数

```python
def __init__(self, db, key):
```

- **`db`**: (`DBSource`) 数据库源实例
- **`key`**: (字符串) 数据键

#### 属性

- `cache`: 缓存的数据字典
- `db`: 数据库源实例
- `key`: 数据键

#### 方法

##### `get(item, default=None)`

获取字典中的项。

- **`item`**: 字典键
- **`default`**: (可选) 默认值，如果键不存在则设置并返回此值
- **返回值**: 项的值

**注意**: 如果键不存在且提供了默认值，会自动设置该键为默认值。

##### `set(key, value)`

设置字典中的项。

- **`key`**: 字典键
- **`value`**: 要设置的值
- **返回值**: 无

**注意**: 设置后会立即保存到数据库。

##### `has(item)`

检查字典是否包含指定键。

- **`item`**: 字典键
- **返回值**: (布尔值) 是否包含该键

##### `batch(updater)`

批量更新字典中的项。

- **`updater`**: (函数) 更新函数，接受三个参数：`(value, key, cache)`
- **返回值**: 无

**更新函数签名**:
```python
def updater(value, key, cache):
    # value: 当前值
    # key: 当前键
    # cache: 整个缓存字典（可修改）
    pass
```

### `DatabaseArrayView`

数组视图类，提供对列表类型数据的便捷访问和操作。

#### 构造函数

```python
def __init__(self, db, key):
```

- **`db`**: (`DBSource`) 数据库源实例
- **`key`**: (字符串) 数据键

#### 属性

- `cache`: 缓存的数据列表
- `db`: 数据库源实例
- `key`: 数据键

#### 方法

##### `get(item, default=None)`

获取数组中的项。

- **`item`**: (整数) 数组索引
- **`default`**: (可选) 默认值，如果索引不存在则设置并返回此值
- **返回值**: 项的值

**注意**: 如果索引不存在且提供了默认值，会自动设置该索引为默认值（可能需要扩展数组）。

##### `set(key, value)`

设置数组中的项。

- **`key`**: (整数) 数组索引
- **`value`**: 要设置的值
- **返回值**: 无

**注意**: 设置后会立即保存到数据库。

##### `batch(updater)`

批量更新数组中的项。

- **`updater`**: (函数) 更新函数，接受三个参数：`(value, index, cache)`
- **返回值**: 无

**更新函数签名**:
```python
def updater(value, index, cache):
    # value: 当前值
    # index: 当前索引
    # cache: 整个缓存列表（可修改）
    pass
```

##### `size()`

获取数组大小。

- **返回值**: (整数) 数组长度

##### `iter()`

获取数组迭代器。

- **返回值**: 列表迭代器

## 使用示例

### 1. 基本字典视图

```python
from ..architect.persistent.common import DBSource, DatabaseView

# 假设有一个实现了 DBSource 的数据库
class MyDatabase(DBSource):
    def getData(self, key):
        # 实现获取数据
        pass
    
    def setData(self, key, value):
        # 实现设置数据
        pass
    
    def removeData(self, key):
        # 实现移除数据
        pass
    
    def clearData(self):
        # 实现清除数据
        pass

# 创建数据库实例
db = MyDatabase()

# 创建字典视图
player_view = db.createView("player_data")

# 使用视图操作数据
player_view.set("name", "Steve")
player_view.set("level", 5)
player_view.set("health", 100)

# 获取数据
name = player_view.get("name")  # "Steve"
level = player_view.get("level")  # 5
health = player_view.get("health")  # 100

# 检查键是否存在
has_name = player_view.has("name")  # True
has_score = player_view.has("score")  # False

# 使用默认值
score = player_view.get("score", 0)  # 0，并自动设置 score=0
```

### 2. 批量操作

```python
from ..architect.persistent.common import DatabaseView

# 创建视图
stats_view = db.createView("player_stats")

# 初始数据
stats_view.set("kills", 10)
stats_view.set("deaths", 3)
stats_view.set("assists", 5)

# 批量更新：将所有数值乘以2
def double_values(value, key, cache):
    if isinstance(value, (int, float)):
        cache[key] = value * 2

stats_view.batch(double_values)

# 结果：kills=20, deaths=6, assists=10
```

### 3. 数组视图

```python
from ..architect.persistent.common import DatabaseArrayView

# 创建数组视图
inventory_view = db.createArrayView("player_inventory")

# 设置数组项（需要确保索引存在）
# 首先初始化数组
inventory_view.cache = ["sword", "shield", "potion", None, None]

# 设置特定位置
inventory_view.set(0, "diamond_sword")
inventory_view.set(3, "bow")

# 获取数组项
item0 = inventory_view.get(0)  # "diamond_sword"
item1 = inventory_view.get(1)  # "shield"
item4 = inventory_view.get(4, "empty")  # "empty"，并自动设置

# 获取数组大小
size = inventory_view.size()  # 5

# 遍历数组
for item in inventory_view.iter():
    if item:
        print(f"物品: {item}")
```

### 4. 游戏数据管理

```python
class GameDataManager:
    def __init__(self, db):
        self.db = db
        self.player_view = db.createView("player")
        self.settings_view = db.createView("settings")
        self.achievements_view = db.createArrayView("achievements")
    
    def initialize_player(self, player_id):
        """初始化玩家数据"""
        self.player_view.set("id", player_id)
        self.player_view.set("level", 1)
        self.player_view.set("experience", 0)
        self.player_view.set("inventory", [])
        self.player_view.set("stats", {"kills": 0, "deaths": 0})
    
    def level_up(self):
        """玩家升级"""
        current_level = self.player_view.get("level", 1)
        self.player_view.set("level", current_level + 1)
        
        # 重置经验
        self.player_view.set("experience", 0)
        
        # 解锁新成就
        self.unlock_achievement(f"reach_level_{current_level + 1}")
    
    def unlock_achievement(self, achievement_name):
        """解锁成就"""
        achievements = self.achievements_view.cache
        if achievement_name not in achievements:
            achievements.append(achievement_name)
            self.achievements_view.cache = achievements
    
    def update_settings(self, **kwargs):
        """更新游戏设置"""
        for key, value in kwargs.items():
            self.settings_view.set(key, value)
    
    def get_player_summary(self):
        """获取玩家摘要"""
        return {
            "id": self.player_view.get("id"),
            "level": self.player_view.get("level", 1),
            "experience": self.player_view.get("experience", 0),
            "achievements": self.achievements_view.cache,
            "settings": self.settings_view.cache
        }
```

### 5. 数据验证和转换

```python
class ValidatedDatabaseView(DatabaseView):
    def __init__(self, db, key, validator=None, transformer=None):
        super().__init__(db, key)
        self.validator = validator
        self.transformer = transformer
    
    def set(self, key, value):
        """设置带验证的数据"""
        # 验证数据
        if self.validator:
            if not self.validator(key, value):
                raise ValueError(f"数据验证失败: key={key}, value={value}")
        
        # 转换数据
        if self.transformer:
            value = self.transformer(value)
        
        # 调用父类方法
        super().set(key, value)
    
    def get(self, item, default=None):
        """获取带转换的数据"""
        value = super().get(item, default)
        
        # 转换返回值
        if self.transformer and value is not None:
            value = self.transformer(value, reverse=True)
        
        return value

# 使用示例
def validate_player_data(key, value):
    """验证玩家数据"""
    if key == "level" and (not isinstance(value, int) or value < 1 or value > 100):
        return False
    if key == "name" and (not isinstance(value, str) or len(value) > 20):
        return False
    return True

def transform_numbers(value, reverse=False):
    """转换数字类型"""
    if reverse:
        # 从存储格式转换回使用格式
        return float(value) if isinstance(value, (int, float)) else value
    else:
        # 从使用格式转换到存储格式
        return str(value) if isinstance(value, (int, float)) else value

# 创建带验证的视图
player_view = ValidatedDatabaseView(
    db, 
    "player_data",
    validator=validate_player_data,
    transformer=transform_numbers
)

# 使用验证视图
try:
    player_view.set("level", 5)  # 成功
    player_view.set("level", 150)  # 抛出 ValueError
    player_view.set("name", "VeryLongPlayerNameThatExceedsLimit")  # 抛出 ValueError
except ValueError as e:
    print(f"数据验证错误: {e}")
```

## 设计模式

### 1. 视图模式 (View Pattern)

`DatabaseView` 和 `DatabaseArrayView` 实现了视图模式，提供对底层数据的抽象访问层。

**优点**:
- 隐藏底层存储细节
- 提供统一的数据访问接口
- 支持数据缓存和批量操作
- 便于数据验证和转换

### 2. 装饰器模式 (Decorator Pattern)

可以通过继承视图类来添加额外功能，如验证、转换、日志等。

### 3. 观察者模式 (Observer Pattern)

视图可以扩展为支持数据变更通知。

```python
class ObservableDatabaseView(DatabaseView):
    def __init__(self, db, key):
        super().__init__(db, key)
        self.observers = []
    
    def add_observer(self, observer):
        """添加观察者"""
        self.observers.append(observer)
    
    def set(self, key, value):
        """设置数据并通知观察者"""
        old_value = self.cache.get(key)
        super().set(key, value)
        
        # 通知观察者
        for observer in self.observers:
            observer.on_data_changed(self.key, key, old_value, value)
```

## 性能考虑

1. **缓存**: 视图在内存中缓存数据，减少数据库访问
2. **批量操作**: `batch` 方法支持批量更新，提高性能
3. **延迟保存**: 可以扩展为支持延迟保存，减少磁盘IO
4. **内存使用**: 大型数据集可能占用较多内存

## 注意事项

1. **数据一致性**: 视图缓存可能与底层数据不同步，需要谨慎处理并发访问
2. **错误处理**: 数组视图的 `get` 方法在索引不存在时会自动扩展数组
3. **默认值**: 使用默认值时会自动设置到数据库中
4. **类型安全**: Python 是动态类型语言，需要自行确保数据类型正确
5. **序列化**: 存储的数据需要支持序列化（如 JSON 序列化）
