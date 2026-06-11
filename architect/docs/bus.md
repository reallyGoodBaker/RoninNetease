# CommandBus — 命令总线

`CommandBus` 是一个本地同步命令总线，用于解耦子系统之间的通信。子系统通过命令名注册处理器，其他模块通过命令名调用，无需直接引用目标子系统实例。

---

## 1. 概述

`CommandBus` 提供了一种**服务定位式**的模块间通信模式：
- **发布者**通过命令名发布任务，不关心谁处理
- **处理者**注册到特定命令名下，独立处理请求
- 一个命令名可以注册**多个处理器**，按注册顺序依次执行

与事件系统和 RPC 的对比：

| 特性 | CommandBus | Event | Remote RPC |
|---|---|---|---|
| 通信方向 | 同步调用 | 异步广播 | 跨端异步 |
| 返回值 | 收集所有处理器返回值 | 通过事件对象传递 | Future 回调 |
| 使用场景 | 模块间服务调用 | 状态变化通知 | 客户端↔服务端 |

---

## 2. API

### 2.1 获取实例

```python
from architect.core.subsystem import SubsystemManager

manager = SubsystemManager.getInstance()
bus = manager.bus  # CommandBus 实例
```

### 2.2 方法

| 方法 | 签名 | 说明 |
|---|---|---|
| `register` | `(command_name: str, handler: callable) -> callable` | 注册处理器，返回注销函数 |
| `execute` | `(command_name: str, *args, **kwargs) -> list` | 执行命令，返回所有处理器返回值列表 |
| `hasCommand` | `(command_name: str) -> bool` | 检查是否有处理器注册 |
| `clearCommand` | `(command_name: str) -> None` | 移除指定命令的所有处理器 |
| `clearAll` | `() -> None` | 移除所有已注册的命令 |

---

## 3. 使用示例

### 3.1 服务端：注册处理器

```python
from architect.core import SubsystemServer, ServerSubsystem

class SpawnSystem(ServerSubsystem):
    def onInit(self):
        manager = SubsystemManager.getInstance()

        # 注册命令处理器
        self._unregister = manager.bus.register('spawnNpc', self.handle_spawn)

    def handleSpawn(self, template, location, is_global=False):
        """处理生成 NPC 的命令"""
        entityId = self.spawnEntity(
            template,
            location,
            (0, 0),
            isGlobal=is_global
        )
        return entityId

    def onDestroy(self):
        # 清理：注销命令
        if hasattr(self, '_unregister'):
            self._unregister()
```

### 3.2 调用命令

```python
class QuestSystem(ServerSubsystem):
    def spawn_quest_npc(self):
        manager = SubsystemManager.getInstance()

        # 检查命令是否可用
        if not manager.bus.hasCommand('spawnNpc'):
            print('[Quest] Spawn system not available')
            return

        # 执行命令，收集返回值
        results = manager.bus.execute(
            'spawnNpc',
            'minecraft:villager',
            Location((100, 64, 200), 0),
            is_global=False
        )

        # results = ['entityIdAbc123']
        if results:
            print('[Quest] NPC spawned:', results[0])
```

### 3.3 多个处理器

```python
# 两个系统都处理 'on_player_death' 命令
class ScoreSystem(ServerSubsystem):
    def onInit(self):
        SubsystemManager.getInstance().bus.register(
            'on_player_death', self.decrease_score
        )

    def decreaseScore(self, playerId, cause):
        print('[Score] Player lost points')
        return {'score_updated': True}

class LogSystem(ServerSubsystem):
    def onInit(self):
        SubsystemManager.getInstance().bus.register(
            'on_player_death', self.log_death
        )

    def logDeath(self, playerId, cause):
        print('[Log] Player %s died: %s' % (playerId, cause))
        return {'logged': True}

# 执行命令 → 两个处理器都被调用
results = bus.execute('on_player_death', 'player_1', 'fall')
# results = [{'score_updated': True}, {'logged': True}]
```

### 3.4 清理命令

```python
manager = SubsystemManager.getInstance()

# 移除特定命令的所有处理器
manager.bus.clearCommand('spawnNpc')

# 移除所有命令
manager.bus.clearAll()
```

---

## 4. 典型模式

### 4.1 服务提供者模式

```python
class DatabaseSystem(ServerSubsystem):
    def onInit(self):
        bus = SubsystemManager.getInstance().bus
        bus.register('db.save', self.save_data)
        bus.register('db.load', self.load_data)
        bus.register('db.delete', self.delete_data)

    def save_data(self, key, value):
        # ... 保存到数据库
        return True

    def load_data(self, key):
        # ... 从数据库加载
        return {'stored_value'}

    def delete_data(self, key):
        # ... 删除
        return True
```

```python
class AnySystem(ServerSubsystem):
    def savePlayer_data(self):
        bus = SubsystemManager.getInstance().bus
        bus.execute('db.save', 'player_1', {'hp': 100})
```

### 4.2 请求-响应模式

```python
# 提供者
class ConfigSystem(ServerSubsystem):
    def onInit(self):
        SubsystemManager.getInstance().bus.register(
            'config.get', self.get_config
        )

    def get_config(self, key):
        return self.config.get(key, None)

# 消费者
class FeatureSystem(ServerSubsystem):
    def onReady(self):
        results = SubsystemManager.getInstance().bus.execute(
            'config.get', 'max_players'
        )
        self.max_players = results[0] if results else 10
```

---

## 5. 与事件系统的对比

```python
# === CommandBus 方式 ===
# 优点：有返回值，同步调用，适合"请求-响应"
manager.bus.execute('get_playerStats', playerId)
# → [{'hp': 100, 'mana': 50}]

# === Event 方式 ===
# 优点：广播通知，适合"状态变化通知"
self.sendServer('PlayerStatsChanged', {'playerId': playerId})
# → 客户端异步接收
```

**选择建议：**
- 需要**返回值** → 使用 `CommandBus`
- 需要**异步广播**给多个接收者 → 使用 Event
- 需要**跨端通信** → 使用 Remote RPC / sendServer / sendClient

---

## 下一步

- [子系统 (subsystem.md)](subsystem.md) — 子系统生命周期
- [事件系统 (event.md)](event.md) — 事件 API
- [远程调用 (quickstart.md#12-远程调用-rpc)](quickstart.md#12-远程调用-rpc) — RPC 参考