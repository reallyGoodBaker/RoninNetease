# 子系统

## 概念

子系统是业务逻辑的唯一载体。每个子系统负责一个功能域（战斗、背包、任务等），由 `SubsystemManager` 统一管理完整的生命周期。

---

## 定义子系统

```python
from architect.compact import ServerSubsystem, ClientSubsystem, SubsystemServer

@SubsystemServer
class CombatSystem(ServerSubsystem):
    "在服务端运行，包含所有战斗逻辑。"
    pass
```

---

## 生命周期

| 方法 | 调用时机 | 典型用途 |
|------|----------|----------|
| `onInit()` | 当前子系统创建完毕 | 注册监听器、初始化数据结构、设 `canTick=True` |
| `onReady()` | **所有**子系统创建完毕后调用 | 安全获取其他子系统、启动定时器 |
| `onUpdate(dt)` | 每 Tick（需 `canTick=True`） | 核心逻辑更新。`dt` 为上次 Tick 的秒数 |
| `onRender(dt)` | 每帧（**仅客户端**） | 渲染相关逻辑 |
| `onDestroy()` | 子系统被移除时 | 清理资源、注销事件 |

```python
@SubsystemServer
class InventorySystem(ServerSubsystem):

    def onInit(self):
        self.data = {}
        self.canTick = True

    def onReady(self):
        # 所有系统就绪，可获取其他子系统
        other = SubsystemManager.getInstance().getSubsystem(CombatSystem)

    def onUpdate(self, dt):
        # 每 tick 执行
        pass

    def onDestroy(self):
        self.data.clear()
```

---

## 获取子系统实例

```python
from architect.core.subsystem import SubsystemManager

mgr = SubsystemManager.getInstance()
combat = mgr.getSubsystem(CombatSystem)
combat = mgr.getSubsystemByName('CombatSystem')
```

---

## 通信方法

### 服务端 → 客户端 / 全体客户端

```python
class ServerSystem(ServerSubsystem):
    def notify_player(self, pid):
        self.sendClient(pid, 'UpdateInventory', {'slots': [...]})
    def broadcast_message(self, msg):
        self.sendAllClients('ChatMsg', {'text': msg})
```

### 客户端 → 服务端

```python
class ClientSystem(ClientSubsystem):
    def request_purchase(self, item_id):
        self.sendServer('BuyItem', {'itemId': item_id})
```

---

## 快捷代理: `subsystem`（小写类）

```python
from architect.core.subsystem import subsystem

# 无需获取具体子系统实例——框架自动代理第一个注册的子系统
subsystem.sendServer('RequestItem', {'itemId': 'diamond'})
subsystem.spawnServerEntity('minecraft:zombie', loc, (0, 0))
```

当模组中只有一个服务端子类、一个客户端子类时，`subsystem` 提供了最简洁的 API。
多子系统场景请使用 `SubsystemManager.getSubsystem(YourClass)` 获取精确实例。

---

## `@Internal` 访问控制 — v1.1.0

标记为 `@Internal` 的方法禁止被外部子系统直接调用，必须通过 CommandBus 或事件系统间接访问。

```python
from architect.core.subsystem import Internal

class CombatSystem(ServerSubsystem):

    @Internal
    def compute_damage(self, attacker_id, target_id):
        "内部计算逻辑。其他系统请走 bus.execute('compute_damage')。"
        return {'effective': 50}
```

---

## 固定频率调度器

```python
class AutoSaveSystem(ServerSubsystem):

    def onInit(self):
        self.scheduleFixed('save', period=5)  # 每 5 秒执行一次

    @Sched.Fixed('save')
    def auto_save(self):
        print('自动保存中...')
```