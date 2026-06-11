# Persona — 渲染覆盖系统

Persona 系统用于在客户端动态修改实体的渲染外观（模型、贴图、材质、动画、粒子等），并通过客户端 ↔ 服务端事件系统同步渲染变化。

---

## 1. 概述

```
architect.utils.persona
├── client.py    ← PersonaRendererComponent, PersonaEventsSubsystem, 辅助函数
└── server.py    ← PersonaServer（服务端同步中继）
```

---

## 2. PersonaRendererComponent — 客户端渲染组件

### 2.1 获取组件

```python
from architect.utils.persona.client import (
    PersonaRendererComponent, createPersona, getPersona
)
from architect.component import getOrCreateComponent

# 创建或获取渲染组件
persona = createPersona(entityId)
persona = getPersona(entityId)
persona = getOrCreateComponent(entityId, PersonaRendererComponent)
```

### 2.2 完整 API

`PersonaRendererComponent` 所有公共方法：

| 方法 | 说明 |
|---|---|
| `addRenderConf(jsonObject, rebuild=True)` | 添加渲染定义（自动判断玩家/非玩家） |
| `changeRenderConf(jsonObject, broadcast=True, full=False)` | 修改渲染（`full=False` 只改 animations/scripts；`full=True` 改全部） |
| `resetRenderConf(broadcast=True, rebuild=True)` | 重置为默认渲染 |
| `rebuildRender()` | 重建渲染 |
| `showHand(visible=True, mode=0)` | 控制手部显示 |
| `shadowPlayerRootAnim(anim=None)` | 遮蔽玩家根动画，可选自定义动画替代 |
| `restorePlayerRootAnim()` | 恢复根动画控制器 |

**`addRenderConf(jsonObject, rebuild=True)`** — 首次加载时使用（添加模式）。`jsonObject` 支持的键：

```python
{
    "geometry":  {"default": "geometry.mymodel"},         # 模型
    "textures":  {"default": "textures/entity/mytexture"}, # 贴图
    "materials": {"default": "entity_alphatest"},          # 材质
    "animations": {                                        # 动画 / 动画控制器
        "root": "controller.animation.player.root",       # controller. 前缀 = 动画控制器
        "idle": "animation.mymodel.idle",                 # 否则 = 普通动画
    },
    "particle_effects": {},                                # 粒子特效
    "sound_effects": {},                                   # 音效
    "render_controllers": [                                # 渲染控制器
        {"controller.render.default": "1"}                 # {name: condition}
    ],
    "scripts": {
        "animate": ["root", "idle"]                        # 动画播放列表
    }
}
```

**`changeRenderConf(jsonObject, broadcast=True, full=False)`** — 运行时动态修改。`full=False`（默认）时只允许修改 `materials`, `animations`, `scripts`, `render_controllers`；`full=True` 时可修改全部字段（含 `geometry`, `textures`, `particle_effects`, `sound_effects`）。`broadcast=True` 时自动广播渲染变更到其他客户端。

**`resetRenderConf(broadcast=True, rebuild=True)`** — 恢复到默认渲染。对于玩家，会移除所有自定义 geometry/animController/renderController 并恢复 `controller.animation.player.root`。

**`shadowPlayerRootAnim(anim=None)`** — 用 `'0'` 遮蔽 `root` 的脚本动画，可选传入一个自定义动画名用 `'1'` 替代。

**`rebuildRender()`** — 根据实体类型（玩家/非玩家）重建渲染。

### 2.3 底层方法（按实体类型）

如果需要精细控制玩家和非玩家的渲染差异：

**玩家渲染：**

| 方法 | 签名 |
|---|---|
| `addPlayerRenderConf(jsonObject, rebuild=True)` | 添加玩家渲染配置 |
| `changePlayerRenderConf(jsonObject={}, full=False, broadcast=True)` | 修改玩家渲染配置 |
| `resetPlayerRenderConf(broadcast=True, rebuild=True)` | 重置玩家渲染 |

**非玩家实体渲染：**

| 方法 | 签名 |
|---|---|
| `addActorRenderConf(jsonObject, actor=None)` | 添加实体渲染（actor 可选指定目标） |
| `changeActorRenderConf(jsonObject, actor=None, full=False, broadcast=True)` | 修改实体渲染 |
| `resetActorRenderConf(broadcast=True)` | 重置实体渲染 |

### 2.4 广播方法

| 方法 | 签名 |
|---|---|
| `broadcastRenderConf(jsonObj={})` | 通过 `PersonaEventsSubsystem` 广播渲染变更到服务端 |
| `broadcastResetConf()` | 广播渲染重置请求 |
| `hasRenderController(name)` | 检查玩家是否已有指定渲染控制器 |

### 2.5 静态方法：类型级别渲染

在加载阶段为所有实体类型应用默认渲染：

```python
# 全局玩家渲染（所有玩家自动应用）
PersonaRendererComponent.addPlayerTypeRenderConf({
    "materials": {"default": "entity_alphatest"},
    "geometry": {"default": "geometry.humanoid.custom"},
})

# 按实体类型渲染
PersonaRendererComponent.addActorTypeRenderConf("minecraft:zombie", zombie_conf)
```

### 2.6 辅助函数与常量

```python
from architect.utils.persona.client import (
    createPersona,   # createComponent(id, PersonaRendererComponent)
    getPersona,      # getOneComponent(id, PersonaRendererComponent)
    PlayerDefaultClientDef,  # 原版玩家默认渲染定义（dict，可直接用作模板）
    RenderConfKeys,  # 支持的渲染配置键 tuple
    PlayerActorTypes,  # ('minecraft:player', 'player')
)
```

### 2.7 完整示例

```python
from architect.utils.persona.client import (
    PersonaRendererComponent, createPersona, getPersona, PlayerDefaultClientDef
)
from architect.core import SubsystemClient, EventListener, localPlayerId

@SubsystemClient
class MySkinSystem(ClientSubsystem):
    # 自定义模型配置
    warrior_conf = {
        "geometry": {"default": "geometry.warrior"},
        "textures": {"default": "textures/entity/warrior"},
        "animations": {
            "root": "controller.animation.player.root",
            "idle": "animation.warrior.idle",
        },
        "scripts": {"animate": ["root", "idle"]}
    }

    @EventListener('OnLocalPlayerStopLoading')
    def onLoad(self, ev):
        persona = createPersona(localPlayerId())
        # 首次加载使用 addRenderConf
        persona.addRenderConf(self.warrior_conf)

    def switch_to_attack_anim(self):
        persona = getPersona(localPlayerId())
        # 切换动画（不重建 geometry/texture）
        persona.changeRenderConf({
            "animations": {
                "attack": "animation.warrior.attack",
            },
            "scripts": {"animate": ["attack"]}
        })

    def reset(self):
        persona = getPersona(localPlayerId())
        persona.resetRenderConf()
```

---

## 3. PersonaEventsSubsystem — 客户端事件子系统

自动注册为 `@SubsystemClient`，处理以下角色变更：

| 事件 | 处理 |
|---|---|
| `PersonaChangeServer` | 服务端请求修改渲染 → `changeRenderConf(event.data, broadcast=False, full=True)` |
| `PersonaResetServer` | 服务端请求重置 → `resetRenderConf(broadcast=False)` |
| `PersonaChangeClientAuthed` | 已认证的客户端修改广播 |
| `PersonaResetClientAuthed` | 已认证的客户端重置广播 |
| `OnLocalPlayerStopLoading` | 本地玩家加载完成 → 创建 Persona + 发送 `PersonaChangeClientInit` |
| `AddPlayerCreatedClientEvent` | 其他玩家创建 → 创建 Persona |

---

## 4. PersonaServer — 服务端中继子系统

```python
from architect.utils.persona.server import PersonaServer

# 自动注册为 @SubsystemServer

@SubsystemServer
class PersonaServer(ServerSubsystem):
    # 服务端直接修改玩家渲染 → 广播到所有客户端
    def changePersona(self, id, renderConf)
    def resetPersona(self, id)

    # 事件监听（客户端 → 服务端 → 其他客户端）
    @EventListener('BroadcastPersonaChange', isCustomEvent=True)
    def onPersonaChangeClient(self, ev)

    @EventListener('BroadcastPersonaReset', isCustomEvent=True)
    def onPersonaResetClient(self, ev)

    @EventListener('PersonaChangeClientInit', isCustomEvent=True)
    def onPersonaChangeClientInit(self, ev)
```

---

## 5. 完整示例

```python
# 客户端：切换玩家模型
from architect.utils.persona.client import (
    PersonaRendererComponent, createPersona, getPersona
)
from architect.core import SubsystemClient, EventListener

@SubsystemClient
class MySkinSystem(ClientSubsystem):
    warrior_conf = {
        "geometry": {"default": "geometry.warrior"},
        "textures": {"default": "textures/entity/warrior"},
        "animations": {
            "root": "controller.animation.player.root",
            "idle": "animation.warrior.idle",
        },
        "scripts": {"animate": ["root", "idle"]}
    }

    @EventListener('OnLocalPlayerStopLoading')
    def onLoad(self, ev):
        persona = getPersona(localPlayerId())
        if persona:
            persona.changeRenderConf(self.warrior_conf, full=True)

    def resetToDefault(self):
        persona = getPersona(localPlayerId())
        if persona:
            persona.resetRenderConf()
```

```python
# 服务端：触发全体玩家渲染变更
from architect.utils.persona.server import PersonaServer

class MyServerSystem(ServerSubsystem):
    def makeEveryoneWarrior(self):
        persona_server = PersonaServer.getInstance()
        for playerId in getPlayerList():
            persona_server.changePersona(playerId, warrior_conf)
```

---

## 下一步

- [数学库 (math.md)](math.md) — 向量和矩阵
- [组件系统 (ecs.md)](ecs.md) — Component API