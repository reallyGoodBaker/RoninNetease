# UI 系统

## 概念

`UiSubsystem` 是客户端专用于 UI 管理的子系统，内建了**响应式数据绑定**（Signal/Sink）模式，自动追踪数据变化并更新控件。

---

## 定义 UI

```python
from architect.compact import UiSubsystem, Screen, AutoCreate

@Screen       # 标记为全屏 UI
@AutoCreate   # 框架初始化完成后自动创建
class MainScreen(UiSubsystem):
    pass
```

---

## 生命周期

| 方法 | 调用时机 |
|------|----------|
| `onCreate()` | UI 被创建后立即调用（在 Create 中） |
| `onBackPressed()` | 玩家按返回键时调用（返回 True 阻止关闭） |
| `onDestroy()` | UI 被销毁时调用 |

```python
class MainScreen(UiSubsystem):

    def onCreate(self):
        print('UI 已创建')

    def onBackPressed(self):
        "返回 True 可阻止 UI 关闭。"
        return True  # 禁止关闭此屏
```

---

## 控件查找

```python
class MainScreen(UiSubsystem):

    def onCreate(self):
        # 通过路径查找
        btn = self.find('/panel/button')
        # 通过名称查找
        btn = self.findByName('my_button')
        # 根控件
        root = self.rootControl
```

---

## 响应式数据绑定 (Signal/Sink)

```python
from architect.compact import signal, Sink

class HUD(UiSubsystem):

    def onCreate(self):
        # signal 返回 (getter, setter) 元组
        self.get_score, self.set_score = signal(0)
        self.get_name, self.set_name = signal('Player1')

    @Sink
    def update_display(self):
        "当依赖的 signal 值变化时自动重新执行。
        Sink 首次执行时自动追踪所有被 getter() 调用的 signal。"
        label = self.find('/label')
        label.SetText(self.get_name() + ': ' + str(self.get_score()))

    def add_score(self, pts):
        self.set_score(self.get_score() + pts)  # 自动触发 update_display
```

### 原理

1. `@Sink` 装饰的方法首次执行时，`SinkContext` 会追踪所有被调用的 `getter()`
2. 当任意被追踪的 `signal` 通过 `setter()` 更新，`@Sink` 方法自动重新执行
3. 类似 Vue 的 computed / Solid.js 的 createEffect

---

## 手势事件

```python
class MainScreen(UiSubsystem):

    def onCreate(self):
        # 注册按钮点击事件
        self.addEventListener('/btn', 'ButtonTouchUpInsideEvent', self.on_click)

    def on_click(self, event):
        print('按钮被点击:', event.control)
```

支持的手势类型：`ButtonTouchDownEvent`、`ButtonTouchUpEvent`、`ButtonTouchUpInsideEvent`、`ButtonTouchUpOutsideEvent`、`ButtonDragEvent`、`ButtonLongPressEvent`。

---

## 创建/管理

```python
# 获取或创建实例（存在则返回已有）
ui = MainScreen.getOrCreate(param1='val')

# 强制创建（存在则先销毁旧的）
ui = MainScreen.create(param1='val')

# 作为全屏界面 push
ui = MainScreen.pushScreen()

# 关闭
ui.remove()
```