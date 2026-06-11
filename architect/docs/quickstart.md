# 快速开始

本指南从零开始构建一个完整的网易《我的世界》模组，涵盖 RoninNetease v1.1.0 的所有核心 API。

所有 API 均可从 `architect.compact` 按需导入。

---

## 1. 项目结构

```
my_mod/
├── modMain.py              # 模组入口
├── conf.py                 # 配置文件
├── server_system.py        # 服务端子系统
├── client_system.py        # 客户端子系统
├── components.py           # 组件定义
└── architect/              # 框架本体
```

---

## 2. 配置文件 `conf.py`

```python
# conf.py — 必须定义引擎命名空间和系统名称
MOD_ENGINE_NAME = 'my_mod'
MOD_SYSTEM_NAME = 'my_system'
```

> 更高级的配置选项（模块列表、插件列表、热更新白名单）详见 `architecture.md` 中的配置覆盖机制章节。

---

## 3. 模组入口 `modMain.py`

```python
# modMain.py
from architect.compact import createServer, createClient

def modInit():
    createServer()   # 启动 SubsystemManager（服务端）
    createClient()   # 启动 SubsystemManager（客户端）
```

---

## 4. 服务端子系统 — 完整示例

```python
# server_system.py
from architect.compact import SubsystemServer, ServerSubsystem, Sched, Query, EntityId

# ===== 组件定义 =====
from architect.component import Component, BaseCompServer
from architect.component.schema import FieldSchema, DefineFields

@Component()
@DefineFields(
    health=FieldSchema(default=100, validator=lambda v: 0 <= v <= 1000),
    name=FieldSchema(default='unnamed'),
)
class HealthComponent(BaseCompServer):
    "血量数据结构，字段由框架自动初始化。"
    def onCreate(self, entityId):
        self.max_health = self.health  # 额外初始化
    def onDestroy(self, entityId):
        pass

# ===== 子系统定义 =====
@SubsystemServer
class HealthSystem(ServerSubsystem):

    def onInit(self):
        self.canTick = True          # 必须设为 True 才能驱动 @Query 方法
        print('[Server] HealthSystem 初始化完毕')

    def onReady(self):
        """所有子系统创建完毕后调用。"""
        print('[Server] 所有系统已就绪')

    @Sched.Tick()
    @Query(HealthComponent, EntityId)
    def process_health(self, entityId, health):
        """每个 Tick 自动遍历所有拥有 HealthComponent 的实体。"""
        if health.health <= 0:
            self.destroyEntity(entityId)
            print('实体已死亡:', entityId)

    def onDestroy(self):
        print('[Server] HealthSystem 已销毁')
```

---

## 5. 客户端子系统

```python
# client_system.py
from architect.compact import SubsystemClient, ClientSubsystem, Sched

@SubsystemClient
class RenderSystem(ClientSubsystem):

    def onInit(self):
        self.canTick = True

    @Sched.Render()
    def onRender(self, args):
        "每个渲染帧执行（60tps 环境约 60fps）"
        pass

    def sendServer(self, eventName, eventData):
        self.system.NotifyToServer(eventName, eventData)
```

---

## 6. 事件监听

```python
from architect.compact import EventListener, ChainedEvent

class MonsterSystem(ServerSubsystem):

    @EventListener('EntityDeathEvent')
    def on_entity_death(self, event):
        "event 是一个 ChainedEvent 对象。"
        dead_id = event.entityId
        # 阻止后续监听器被调用
        event.stop()
        # 或者阻止引擎默认行为
        event.prevent()
```

### 自定义事件

```python
from architect.compact import CustomEvent

class QuestSystem(ServerSubsystem):

    @CustomEvent('QuestCompleted')
    def on_quest_done(self, event):
        player = event.playerId
        reward = event.reward
        print('任务完成:', player, reward)
```

---

## 7. 远程调用 RPC

### 服务端暴露方法

```python
from architect.compact import Remote

class GameSystem(ServerSubsystem):

    @Remote(itemId=str, amount=lambda v: isinstance(v, int) and v > 0)
    def give_item(self, playerId, itemId, amount):
        "playerId 由框架自动注入。itemId/amount 在服务端验证参数类型。"
        pass
```

### 客户端调用

```python
from architect.compact import remote

# 发送消息不等待返回
remote.client.call('GameSystem.give_item', 'diamond', 10)

# 异步调用并等待结果
future = remote.client.invoke('GameSystem.get_score')
future.done(lambda score: print('分数:', score))
```

---

## 8. 响应式 UI

```python
from architect.compact import UiSubsystem, signal, Sink, Screen, AutoCreate

@Screen
@AutoCreate
class MainScreen(UiSubsystem):

    def onCreate(self):
        self.get_score, self.set_score = signal(0)

    @Sink
    def update_label(self):
        "当依赖的 signal 变化时自动重新执行。"
        label = self.find('/label')
        label.SetText('Score: ' + str(self.get_score()))

    def add_points(self, pts):
        self.set_score(self.get_score() + pts)
```

---

## 9. 插件系统

```python
from architect.compact import Plugin, PluginBase

@Plugin('myPlugin', ver=[1, 0, 0], deps={'basePlugin': '>=1.0.0'})
class MyPlugin(PluginBase):

    def onCreate(self):
        pass

    def onAttach(self, manager):
        print('插件已挂载')

    def onDestroy(self):
        print('插件已卸载')
```

---

## 10. 性能诊断 Profiler

```python
from architect.core.profiler import profiler

# 包裹任何代码块进行计时
with profiler.record('expensive_logic'):
    do_work()

# 在子系统中定期导出快照
class DebugSystem(ServerSubsystem):
    def onUpdate(self, dt):
        snap = profiler.flush()
        # { 'scheduler.tickSkipped': {'avg_ms': 0.0, ...}, ... }
        for k, s in snap.items():
            if s['max_ms'] > 16:
                print('[PERF]', k, s['avg_ms'], 'ms')
```

---

## 11. CommandBus 解耦子系统

```python
from architect.core.subsystem import SubsystemManager

mgr = SubsystemManager.getInstance()

# Provider 注册
mgr.bus.register('enemy_killed', lambda boss_id: print('boss defeated:', boss_id))

# Consumer 调用
mgr.bus.execute('enemy_killed', 'dragon')
```

---

## 完整 API 索引

| 模块 | 代表性导出 |
|------|-----------|
| **architect.compact** | 统一入口，包含以下所有 |
| Subsystem | `SubsystemServer`, `SubsystemClient`, `Internal` |
| Scheduler | `Sched`, `Scheduler`, `Future`, `Async` |
| Component | `Component`, `createComponent`, `hasComponent`, `Marker` |
| Component Schema | `FieldSchema`, `DefineFields` |
| Query | `Query`, `EntityId`, `ExtraArguments`, `ExtraArgDict` |
| Event | `EventListener`, `CustomEvent`, `ChainedEvent` |
| Remote | `Remote`, `remote.client`, `remote.server` |
| UI | `UiSubsystem`, `signal`, `Sink`, `Screen`, `AutoCreate` |
| Plugin | `Plugin`, `PluginBase`, `getPlugin` |
| CommandBus | `CommandBus` (通过 `SubsystemManager.bus` 访问) |
| Profiler | `Profiler`, `profiler` |
| Config | `modConf()` 获取/修改框架和模组配置 |
| Math | `vec3`, `mat4`, `vec4`（详见 math.md） |