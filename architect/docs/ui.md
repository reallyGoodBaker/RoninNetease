# UI 系统 (UiSubsystem)

`UiSubsystem` 是一个结合了引擎 `ScreenNode` 的强大基类，它提供了响应式数据绑定、自动化控件查找和手势支持。

## UI 注册与定义

使用装饰器定义 UI 类：

```python
from ..architect.ui.client import UiSubsystem, UiDef, Screen, Hud, AutoCreate

@UiDef('my_layout.json') # 绑定 UI 资源路径
@Screen                  # 标记为全屏界面 (PushScreen)
@AutoCreate              # 脚本加载后自动创建实例
class MyPanel(UiSubsystem):
    def onCreate(self):
        # UI 创建后的回调
        pass

    def onDestroy(self):
        # UI 销毁前的回调
        pass

    def onBackPressed(self):
        # 返回键按下时的逻辑，返回 True 可阻止默认关闭行为
        return False
```

## 响应式数据绑定 (Signal & Sink)

`architect` 的 UI 系统支持细粒度的响应式更新，避免手动操作控件。

### signal (信号)
定义一个状态，它返回一个 (getter, setter) 元组。
```python
from ..architect.ui.client import signal

class MyPanel(UiSubsystem):
    # 定义名称状态，默认值为 "Guest"
    get_name, set_name = signal("Guest")
```

### Sink (响应器)
使用 `@Sink` 装饰的方法会追踪其内部调用的所有信号 getter。当信号值改变时，该方法会自动重新执行。
```python
from ..architect.ui.client import Sink

@Sink
def update_ui(self):
    name = self.get_name() # 自动建立依赖
    self.find('/name_label').set_text(name)
```

### reactive (对象响应式)
用于使整个对象属性变为响应式（仅限继承自 `object` 的新式类）。
```python
from ..architect.ui.client import reactive

# 在 __init__ 或某处
self.get_data, self.set_data = reactive(my_obj)
```

## 控件操作

- **self.find(path)**: 获取指定路径的控件实例。内部会自动缓存已找到的控件。
- **self.findByName(name)**: 通过名称查找子控件。
- **self.remove()**: 关闭并移除当前 UI。如果是 Screen 则自动 PopScreen。

## 手势绑定 (@UI_GESTURE)

配合 `architect.ui.gesture` 模块，可以通过装饰器直接绑定手势：

```python
from ..conf import UI_GESTURE

@UI_GESTURE('Tap', '/touch_area')
def on_tap(self):
    print("Tapped!")
```

## 全局 API

- `UiSubsystem.getOrCreate(**params)`: 获取单例实例，不存在则创建。
- `UiSubsystem.create(**params)`: 创建新实例。
- `UiSubsystem.pushScreen(**params)`: 推入全屏界面。
