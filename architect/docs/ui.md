# UI — 用户界面系统

RoninNetease 的 UI 系统提供声明式的 UI 管理，核心包括 `UiSubsystem`、响应式数据绑定（`Signal`/`Sink`）和触摸手势识别。

---

## 1. 架构

```
architect.ui
├── client.py    ← UiSubsystem, UiDef, Sink, AutoCreate, signal, Screen, Ui
└── gesture.py   ← Touch, TouchPhase 手势识别
```

UI 系统**仅用于客户端**。`UiSubsystem` 继承自 `ClientSubsystem`。

---

## 2. 核心概念

| 概念 | 说明 |
|---|---|
| `UiSubsystem` | UI 子系统基类（继承 `ClientSubsystem`） |
| `@UiDef(uiname)` | 声明 UI 的命名空间（对应 UI JSON 中的 namespace） |
| `@Screen(name)` | 声明 UI 屏幕名称 |
| `@AutoCreate` | 标记 UI 初始化方法为自动创建 |
| `@Sink(initiator)` | 标记更新 UI 的方法，自动追踪依赖 |
| `signal` | 属性装饰器，创建可被追踪的信号值 |
| `Ui` | UI 实例封装（底层引擎 UI 对象的包装） |
| `Touch` | 触摸手势识别器 |

---

## 3. `UiSubsystem` — UI 子系统基类

```python
from architect.ui.client import UiSubsystem, UiDef, Sink, AutoCreate
from architect.ui.client import signal, Screen, Ui

class MyHUD(UiSubsystem):
    canTick = True

    # === 3.1 声明 UI ===

    @UiDef('my_hud')      # UI JSON 中的 namespace
    @Screen('hud_screen') # UI 屏幕名称
    @AutoCreate           # 首次加载时自动创建
    def initHUD(self, ui: Ui):
        """
        UI 创建时调用。
        ui 是一个 Ui 对象，封装了底层引擎 UI 功能。
        """
        self.hud = ui

    # === 3.2 响应式数据 ===

    @signal
    def hp(self):
        """signal 属性：返回当前 HP 值"""
        return self.player_health

    hp_signal = hp  # signal 的描述符对象

    # === 3.3 响应式 UI 更新 ===

    @Sink(initiator=hp)
    def updateHpBar(self):
        """当 hp 值变化时自动触发"""
        if hasattr(self, 'hud'):
            self.hud.set_text('hp_label', str(self.hp_value))
            self.hud.set_bar('hp_bar', self.hp_value / self.max_hp)

    # === 3.4 Tick 更新 ===

    def onUpdate(self, dt):
        """每帧检查数据变化"""
        if self.hp_value != self.last_hp:
            self.last_hp = self.hp_value
            # signal 机制会自动触发 @Sink 方法
```

---

## 4. 响应式数据绑定

### 4.1 `@signal` — 信号属性

`@signal` 将方法转换为信号属性。它内部使用描述符协议（`__get__` / `__set__`）：

```python
class MyHUD(UiSubsystem):
    @signal
    def hp(self):
        return self._hp

    @signal
    def mana(self):
        return self._mana

    def onUpdate(self, dt):
        # 读取信号值（触发追踪）
        current_hp = self.hp_value    # 获取 current value
        current_mana = self.mana_value
```

`@signal` 装饰的方法必须返回一个值。框架会将其转换为一个**可追踪的观察点**。

### 4.2 `@Sink` — 响应回调

`@Sink(initiator=signal_prop)` 将方法绑定到某个信号。当信号值变化时，方法被自动调用：

```python
@Sink(initiator=hp)  # hp 是 @signal 定义的描述符
def refreshUI(self):
    """hp 值变化时自动调用"""
    self.hud.set_text('hp_display', str(self.hp_value))
```

**SinkContext 依赖追踪：**

框架使用 `SinkContext` 上下文管理器追踪 `@Sink` 方法执行期间访问了哪些信号的当前值。这实现了细粒度的依赖追踪，只在真正依赖的数据变化时才触发更新。

### 4.3 追踪机制

```
@Sink(initiator=hp)
def updateUI(self):
    val = self.hp_value      # ← 访问 .hp_value 时，SinkContext.recordDep(hp_signal)
    val = self.mana_value    # ← 也记录 mana_signal
    self.hud.set_text('hp', str(val))

# hp 变化 → 触发 updateUI
# mana 变化 → 也触发 updateUI（因为 updateUI 执行时访问了 mana_value）
```

---

## 5. `Ui` 对象

`Ui` 是底层引擎 UI 对象的封装，提供以下功能：

```python
class Ui:
    def bind(control_path, property_name, signal_or_value)
    def set_text(control_path, text)
    def set_visible(control_path, visible)
    def set_enable(control_path, enable)
    def get_control(control_path)
    def send_event(event_name, data)
    # ... 更多代理方法
```

**示例：**

```python
class MyHUD(UiSubsystem):
    @UiDef('main_hud')
    @Screen('hud_screen')
    @AutoCreate
    def createUI(self, ui: Ui):
        # 设置文本
        ui.set_text('player_name', 'Steve')

        # 控制显示
        ui.set_visible('damage_overlay', False)

        # 启用/禁用
        ui.set_enable('attack_button', True)

        # 绑定信号
        ui.bind('hp_text', 'text', self.hp_signal)
```

---

## 6. 触摸手势 — `Touch`

```python
from architect.ui.gesture import Touch

class GestureHandler(UiSubsystem):
    def onInit(self):
        self.touch = Touch(self.system)

    @Sched.Tick()
    def handle_touch(self):
        # 检测长按
        if self.touch.is_long_press('area_button', duration=0.5):
            print('Long press detected!')

        # 检测滑动
        direction = self.touch.get_swipe_direction('drag_area')
        if direction == 'left':
            print('Swiped left!')

        # 检测点击
        if self.touch.is_tap('click_button'):
            print('Button tapped!')
```

`Touch` 类提供：
- `is_tap(control_path)` — 检测点击
- `is_long_press(control_path, duration)` — 检测长按
- `get_swipe_direction(control_path)` — 获取滑动方向
- 其他触摸相位（began、moved、ended、canceled）检查

---

## 7. UI 生命周期

```
AutoCreate 方法调用 → Ui 实例创建 → Sink 绑定 → Tick 更新 → 响应式刷新
```

1. 引擎 UI 加载完毕后，`@AutoCreate` 标记的方法被调用
2. `Ui` 对象被传入，用于绑定控件和信号
3. 每帧 `onUpdate(dt)` 中检查数据变化
4. 信号值变化触发 `@Sink` 方法，自动刷新 UI

---

## 8. 完整示例：HUD 系统

```python
from architect.ui.client import (
    UiSubsystem, UiDef, Sink, AutoCreate, signal, Screen, Ui
)
from architect.core import SubsystemClient, Sched

class PlayerHUD(UiSubsystem):
    canTick = True

    def onInit(self):
        self.player_name = 'Steve'
        self._hp = 100
        self._max_hp = 100
        self._mana = 50
        self._max_mana = 100
        self._gold = 0
        self.hud = None  # type: Ui

    # === Signals ===

    @signal
    def hp(self):
        return self._hp / max(1, self._max_hp)

    @signal
    def mana(self):
        return self._mana / max(1, self._max_mana)

    @signal
    def gold(self):
        return self._gold

    # === UI Definition ===

    @UiDef('player_hud')
    @Screen('game_hud')
    @AutoCreate
    def createHUD(self, ui: Ui):
        self.hud = ui
        ui.set_text('player_name', self.player_name)

    # === Reactive Bindings ===

    @Sink(initiator=hp)
    def refresh_hp(self):
        if self.hud:
            self.hud.set_bar('hp_bar', self.hp_value * 100)

    @Sink(initiator=mana)
    def refresh_mana(self):
        if self.hud:
            self.hud.set_bar('mana_bar', self.mana_value * 100)

    @Sink(initiator=gold)
    def refresh_gold(self):
        if self.hud:
            self.hud.set_text('gold_text', str(self.gold_value))

    # === Game Logic ===

    def set_health(self, hp, max_hp):
        self._hp = hp
        self._max_hp = max_hp

    def set_mana(self, mana, max_mana):
        self._mana = mana
        self._max_mana = max_mana

    def add_gold(self, amount):
        self._gold += amount

    def onDestroy(self):
        self.hud = None
```

---

## 9. 配置常量

框架在 `conf.py` 中定义了 UI 相关的注解键：

```python
UI_NAMESPACE = 'xxx_roninUi_xxx'    # UI 命名空间前缀
UI_DEF = '_ui_def'                   # @UiDef 注解键
UI_SINK = '_ui_binder'              # @Sink 注解键
UI_SCREEN = '_ui_screen'            # @Screen 注解键
UI_HUD = '_ui_hud'                  # HUD 标记
UI_GESTURE = '_ui_gesture'          # 手势类型标记
```

---

## 下一步

- [子系统 (subsystem.md)](subsystem.md) — 子系统生命周期
- [事件系统 (event.md)](event.md) — 事件监听
- [最佳实践 (best-practices.md)](best-practices.md) — 响应式 UI 设计建议