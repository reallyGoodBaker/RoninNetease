# UI — 用户界面系统

RoninNetease 的 UI 系统提供声明式的 UI 管理，核心包括 `UiSubsystem`、响应式数据绑定（`signal`/`Sink`）和触摸手势识别。

---

## 1. 架构

```
architect.ui
├── client.py    ← UiSubsystem, UiDef, Sink, AutoCreate, Screen, Hud, signal, reactive
└── gesture.py   ← Touch, GestureBinder, TouchEvents
```

UI 系统**仅用于客户端**。`UiSubsystem` 继承自 `ScreenNode + ClientSubsystem + EventTarget`。

---

## 2. 核心概念

| 概念 | 说明 |
|---|---|
| `UiSubsystem` | UI 子系统基类（同时继承 ScreenNode、ClientSubsystem、EventTarget） |
| `@UiDef(uiname)` | **类装饰器**：声明 UI 的命名空间 |
| `@Screen` | **类装饰器**：标记为全屏界面 |
| `@Hud` | **类装饰器**：标记为 HUD 界面 |
| `@AutoCreate` | **类装饰器**：自动创建 UI |
| `@Sink` | **方法装饰器**：标记响应式更新方法，无参数 |
| `signal(default, updater)` | **函数**（非装饰器）：返回 `(getter, setter)` 元组 |
| `reactive(obj)` | **函数**：包装对象为响应式，返回 `(getter, setter)` |

---

## 3. `UiSubsystem` — UI 子系统基类

### 3.1 声明 UI

`@UiDef`、`@Screen`、`@Hud`、`@AutoCreate` 都是**类装饰器**：

```python
from architect.ui.client import UiSubsystem, UiDef, Sink, signal, Screen, AutoCreate, Hud

@UiDef('myHud')      # 类装饰器：声明 UI 命名空间
@Screen               # 类装饰器：标记为全屏界面（或 @Hud 标记为 HUD）
@AutoCreate           # 类装饰器：自动在 UiInitFinished 后创建
class MyHUD(UiSubsystem):
    canTick = True

    def onCreate(self):
        """引擎回调：UI 创建时调用（等效于 Create 事件）"""
        # signal() 返回 (getter, setter) 元组
        self.hpGet, self.hpSet = signal(100)
        self.nameGet, self.nameSet = signal('Steve')

        # 获取控件
        label = self.find('/hpLabel')
        self.find('/attackButton').SetVisible(True)

    @Sink  # 方法装饰器：追踪内部访问的所有 signal
    def refresh(self):
        """任何 signal 变化时自动调用"""
        hp = self.hpGet()
        name = self.nameGet()
        self.find('/hpLabel').SetText(str(hp))

    def onBackPressed(self):
        """返回键被按下，返回 True 阻止关闭界面"""
        return False

    def onDestroy(self):
        """UI 销毁时调用"""
        pass
```

### 3.2 `UiSubsystem` 核心方法

| 方法 | 说明 |
|---|---|
| `self.find(path)` | 按路径查找控件 |
| `self.findByName(name)` | 按名称查找控件 |
| `self.getOrCreate(**params)` | 获取或创建 UI 实例 |
| `self.create(**params)` | 强制重建 UI 实例 |
| `self.pushScreen(**params)` | 以全屏模式 push UI |
| `self.remove()` | 关闭 UI |
| `self.addEventListener(path, type, handler)` | 注册控件事件监听 |
| `self.GetBaseUIControl(path)` | 获取底层引擎控件对象 |

### 3.3 生命周期钩子

| 钩子 | 说明 |
|---|---|
| `onCreate()` | UI 创建时调用 |
| `onBackPressed()` | 返回键被按下，返回 `True` 阻止关闭 |
| `onDestroy()` | UI 销毁时 |
| `Destroy()` | 引擎回调，框架自动调用 `onDestroy()` 并移除子系统 |

---

## 4. 响应式数据绑定

### 4.1 `signal(defaultValue, updater)` — 创建响应信号

**`signal()` 不是装饰器**，它返回 `(getter, setter)` 元组：

```python
from architect.ui.client import signal

# 创建信号（在 onCreate 或 onInit 中）
hpGet, hpSet = signal(100)        # 默认值 100
nameGet, nameSet = signal('')     # 默认值空串

# 读取
current_hp = hp_get()

# 写入（变化时自动触发 @Sink 方法）
hp_set(80)

# 带 updater 的信号（用于可变对象）
stats_get, stats_set = signal(
    {'hp': 100, 'mp': 50},
    updater=lambda new, old: {**old, **new}  # 合并更新
)
```

### 4.2 `@Sink` — 响应式方法

`@Sink` 标记一个方法，在初始化时自动执行一次收集依赖，之后每当内部访问的 signal 值变化时自动重新调用：

```python
@Sink  # 注意：无参数
def refreshUI(self):
    """内部访问 hp_get() 和 name_get()，两个 signal 都会自动追踪"""
    hp = self.hpGet()
    name = self.nameGet()
    self.find('/hpLabel').SetText(str(hp))
    self.find('/nameLabel').SetText(name)
```

### 4.3 依赖追踪机制

```
@Sink 方法首次执行（在 UiSubsystem.Create 中 _initSinks）：
    → 创建 SinkContext(method)
    → 方法执行时调用 hp_get() → SinkContext 记录 hp 的 EventSignal
    → 方法执行时调用 name_get() → SinkContext 记录 name 的 EventSignal

此后：
    → hp_set(80) → hp 的 EventSignal.emit() → 触发 refreshUI
    → name_set('Alice') → name 的 EventSignal.emit() → 触发 refreshUI
```

### 4.4 `reactive(obj)` — 对象级别响应

```python
from architect.ui.client import reactive

data = {'hp': 100, 'mp': 50}
data_get, data_set = reactive(data)

data_set({'hp': 80, 'mp': 50})  # 设置新值
```

---

## 5. 触摸手势

RoninNetease 的触摸手势系统基于**按钮控件事件**，底层使用引擎的 `asButton().SetButtonTouch*Callback` 方法。提供 6 种手势类型，支持装饰器和编程式两种注册方式。

### 5.1 手势类型

`TouchEvents` 是一个字符串元组，包含所有可用类型：

```python
from architect.ui.gesture import TouchEvents

TouchEvents  # ('click', 'down', 'move', 'movein', 'moveout', 'cancel')
```

| 类型 | 引擎回调 | 触发条件 |
|---|---|---|
| `'click'` | `SetButtonTouchUpCallback` | 按钮上松手（按下后在同一控件释放） |
| `'down'` | `SetButtonTouchDownCallback` | 按钮按下 |
| `'move'` | `SetButtonTouchMoveCallback` | 手指在按钮上移动 |
| `'movein'` | `SetButtonTouchMoveInCallback` | 手指从外部移入按钮区域 |
| `'moveout'` | `SetButtonTouchMoveOutCallback` | 手指从按钮区域移出 |
| `'cancel'` | `SetButtonTouchCancelCallback` | 触摸被系统取消 |

### 5.2 事件对象

手势回调接收一个 `ChainedEvent` 对象，其属性：

| 属性 | 说明 |
|---|---|
| `ev.x` | 触摸 X 坐标（屏幕像素） |
| `ev.y` | 触摸 Y 坐标（屏幕像素） |
| `ev.pos` | `(x, y)` 元组 |
| `ev.target` | 转换后的控件对象（`asButton()` 结果） |
| `ev.control` | 原始控件对象 |
| `ev.screen` | 当前 UiSubsystem 实例 |

### 5.3 方式一：装饰器注册（推荐）

```python
from architect.ui.gesture import Touch
from architect.ui.client import UiSubsystem

class MyHUD(UiSubsystem):
    @Touch.Click('/btn_attack')
    def onAttack(self, ev):
        """点击攻击按钮"""
        print('Attack clicked at', ev.x, ev.y)

    @Touch.Down('/btn_jump')
    def onJumpDown(self, ev):
        """按下跳跃按钮"""
        self.startJumpCharge()

    @Touch.Move('/drag_area')
    def onDrag(self, ev):
        """拖拽区域移动"""
        dx = ev.x - self.lastX
        dy = ev.y - self.lastY
        self.rotateView(dx, dy)
        self.lastX = ev.x
        self.lastY = ev.y

    @Touch.MoveIn('/hotbar')
    def onEnterHotbar(self, ev):
        """手指移入快捷栏"""
        print('Entered hotbar at', ev.pos)

    @Touch.MoveOut('/hotbar')
    def onLeaveHotbar(self, ev):
        """手指移出快捷栏"""
        print('Left hotbar')

    @Touch.Cancel('/btn_jump')
    def onJumpCancel(self, ev):
        """跳跃被取消（如来电）"""
        self.cancelJumpCharge()
```

`_initGesture()` 在 `Create` 时自动扫描所有 `@Touch.*` 装饰的方法并注册。

### 5.4 方式二：编程式注册

```python
from architect.ui.client import UiSubsystem

class MyHUD(UiSubsystem):
    def onCreate(self):
        # 使用字符串类型直接注册
        self.addEventListener('/btn_attack', 'click', self.onAttack)
        self.addEventListener('/drag_area', 'move', self.onDrag)

        # 可选的第四个参数：AddTouchEventParams 选项
        self.addEventListener('/btn_attack', 'click', self.onAttack, {'touchArea': (0,0,100,100)})

    def onAttack(self, ev):
        print('Clicked at', ev.pos)

    def onDrag(self, ev):
        print('Dragging at', ev.x, ev.y)
```

### 5.5 内部实现

`addEventListener` 对触摸事件做了特殊处理：

```python
def addEventListener(self, controlPath, type, handler, opt=None):
    control = self.find(controlPath)
    if type in TouchEvents:
        control.asButton().AddTouchEventParams(opt)  # 启用触摸事件
    GestureBinder[type](self, control)  # 绑定引擎回调
    # 包装 handler，用 EventTarget.dispatch() 分发
```

---

## 6. 完整示例

```python
from architect.ui.client import (
    UiSubsystem, UiDef, Sink, signal, Screen, AutoCreate
)

@UiDef('playerHud')
@Screen
@AutoCreate
class PlayerHUD(UiSubsystem):
    canTick = True

    def onCreate(self):
        # 创建 signal
        self.hpGet, self.hpSet = signal(100)
        self.maxHp_get, self.maxHp_set = signal(100)
        self.nameGet, self.nameSet = signal('Steve')

    @Sink
    def refreshHP(self):
        hp = self.hpGet()
        maxHp = self.maxHp_get()
        pct = hp / max(1, maxHp) * 100
        self.find('/hpBar').SetText(str(int(pct)) + '%')

    @Sink
    def refreshName(self):
        self.find('/nameLabel').SetText(self.nameGet())

    # 游戏逻辑更新信号
    def update_health(self, hp, maxHp):
        self.hpSet(hp)
        self.maxHp_set(maxHp)

    def onBackPressed(self):
        return False  # 允许关闭

    def onDestroy(self):
        pass
```

---

## 下一步

- [子系统 (subsystem.md)](subsystem.md) — 子系统生命周期
- [事件系统 (event.md)](event.md) — 事件监听
- [最佳实践 (best-practices.md)](best-practices.md) — UI 设计建议