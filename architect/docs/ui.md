# UI 系统

`architect` 的 UI 系统基于网易 Minecraft 模组 SDK 的 `ScreenNode` 封装，提供了声明式的 UI 定义、响应式数据绑定和手势支持。

## UiSubsystem

`UiSubsystem` 继承自 `ScreenNode`、`ClientSubsystem` 和 `EventTarget`，是游戏内 UI 的基础类。

### 定义 UI

使用 `@UiDef` 装饰器指定 UI 的 JSON 定义文件路径：

```python
from architect.ui.client import UiSubsystem, UiDef, Screen, Sink, signal
from architect.ui.client import AutoCreate

@UiDef('uis.my_ui.main')  # UI JSON 定义路径
@Screen                    # 标记为 Screen 类型 UI
@AutoCreate                # 游戏初始化时自动创建
class MyUI(UiSubsystem):

    def onCreate(self):
        self.text = self.find('/root/text')
        self.text.asText().SetText('Hello, World!')

    def onDestroy(self):
        print('UI destroyed')
```

### 创建模式

- **`@Screen`** - 作为 Screen（弹出式界面）显示，自动处理返回键
- **`@Hud`** - 作为 HUD（平视显示器）显示，始终保持在屏幕上
- **不加标记** - 作为普通 UI 创建

### 手动创建

```python
# 创建（如果已存在则先移除再创建）
ui = MyUI.create()

# 获取或创建（单例模式）
ui = MyUI.getOrCreate()

# 弹出 Screen
ui = MyUI.pushScreen()
```

## 控件查找

```python
class MyUI(UiSubsystem):
    def onCreate(self):
        # 按路径查找（带缓存）
        btn = self.find('/root/button')

        # 按名称查找（需要设置 rootControl）
        ctrl = self.findByName('button_name')

        # 获取并操作控件
        self.find('/root/text').asText().SetText('Updated!')
```

## 响应式编程

### signal（信号）

`signal` 创建响应式数据，当数据变化时自动更新绑定的 UI：

```python
from architect.ui.client import signal, Sink

class MyUI(UiSubsystem):
    def onCreate(self):
        self.count_get, self.count_set = signal(0)

    @Sink
    def on_count_changed(self):
        # 当 count 变化时自动调用此方法
        count = self.count_get()  # 读取时自动建立依赖
        self.find('/root/text').asText().SetText(str(count))

    def increment(self):
        self.count_set(self.count_get() + 1)  # 更新会触发重新绑定
```

### reactive（响应式对象）

`reactive` 用于将整个对象的属性变化变为响应式：

```python
from architect.ui.client import reactive

class GameState:
    def __init__(self):
        self.score = 0
        self.level = 1

class MyUI(UiSubsystem):
    def onCreate(self):
        self.state = GameState()
        self.get_val, self.set_val = reactive(self.state)

    @Sink
    def on_state_changed(self):
        score = self.get_val()
        # 当 state 的任何属性变化时触发
```

## 生命周期

```python
class MyUI(UiSubsystem):
    def onCreate(self):
        # UI 创建时调用
        pass

    def onDestroy(self):
        # UI 销毁时调用
        pass

    def onBackPressed(self):
        # 返回键被按下时调用
        # 返回 True 阻止默认返回行为
        return True
```

## 事件监听

```python
class MyUI(UiSubsystem):
    def onCreate(self):
        # 使用添加监听器方式监听引擎事件
        self.listen('PlayerJoinEvent', self.on_player_join)

        # 移除
        self.unlisten('PlayerJoinEvent', self.on_player_join)

    def destroy(self):
        self.remove()  # 销毁 UI
```

### 控件事件监听

```python
from architect.ui.gesture import TouchEvents

class MyUI(UiSubsystem):
    def onCreate(self):
        # 为控件添加触摸/点击事件
        self.addEventListener(
            '/root/button',
            TouchEvents.Click,
            self.on_button_click
        )

    def on_button_click(self, ev):
        print('Button clicked')
```

## 手势绑定

`GestureBinder` 提供了多种手势类型的支持：

```python
from architect.ui.gesture import TouchEvents

# 支持的手势类型：Click, LongPress, Swipe, Scale, Drag, Down, Move, Up