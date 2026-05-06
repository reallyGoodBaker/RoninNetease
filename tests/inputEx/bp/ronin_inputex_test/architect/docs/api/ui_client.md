# 客户端UI (UI Client) API

`architect.ui.client` 模块提供了客户端用户界面的核心功能，包括UI子系统、响应式数据绑定、手势绑定和屏幕管理。

## 依赖

- `..annotation.AnnotationHelper` - 注解助手
- `..conf.UI_DEF`, `UI_SINK`, `UI_NAMESPACE`, `UI_SCREEN`, `UI_HUD`, `UI_GESTURE` - UI配置常量
- `..event.EventSignal`, `EventTarget` - 事件系统
- `..ref.Ref` - 引用包装器
- `..basic.clientApi` - 客户端API
- `..level.client.LevelClient` - 客户端层级管理
- `..subsystem.ClientSubsystem`, `SubsystemManager`, `subsystem` - 子系统管理
- `.gesture.GestureBinder` - 手势绑定器

## 类

### `SinkContext`

数据接收器上下文类，用于管理响应式数据依赖。

#### 类属性

- `contextStack`: 静态列表，存储上下文栈

#### 静态方法

##### `stackTop()`

获取栈顶的上下文。

- **返回值**: 栈顶的 `SinkContext` 实例，如果栈为空则返回 `None`

#### 构造函数

```python
def __init__(self, initiator):
```

- **`initiator`**: 初始化函数
- **功能**: 创建上下文并将其推入栈中，执行初始化函数，然后从栈中弹出

#### 方法

##### `_removeDepListeners()`

移除依赖监听器。

##### `__enter__()`

上下文管理器入口。

##### `recordDep(dep, value)`

记录依赖关系。

- **`dep`**: `EventSignal` 实例
- **`value`**: 依赖值

### `UiSubsystem`

UI子系统类，继承自 `ScreenNode`、`ClientSubsystem` 和 `EventTarget`。

#### 类属性

- `ns`: UI命名空间（来自 `UI_NAMESPACE`）
- `inst`: 静态实例

#### 构造函数

```python
def __init__(self, engine, system, params):
```

- **`engine`**: 引擎实例
- **`system`**: 系统实例
- **`params`**: 参数字典

#### 属性

- `params`: 参数字典
- `rootControl`: 根控件
- `_foundControls`: 已查找的控件缓存
- `_sinks`: 数据接收器字典

#### 类方法

##### `_handleAutoCreate()`

处理自动创建逻辑。

##### `defineUi(uiDef)`

定义UI。

- **`uiDef`**: UI定义
- **返回值**: 注册结果

##### `getOrCreate(**params)`

获取或创建UI实例。

- **`params`**: 参数
- **返回值**: UI实例

##### `create(**params)`

创建UI实例。

- **`params`**: 参数
- **返回值**: UI实例

##### `pushScreen(**params)`

推送屏幕。

- **`params`**: 参数
- **返回值**: UI实例

#### 实例方法

##### `find(path)`

查找控件。

- **`path`**: 控件路径
- **返回值**: 控件实例

##### `findByName(name)`

按名称查找控件。

- **`name`**: 控件名称
- **返回值**: 控件实例

##### `_handleGamepadBack(ev)`

处理游戏手柄返回事件。

##### `_handleKeyboardBack(ev)`

处理键盘返回事件。

##### `_initSinks()`

初始化数据接收器。

##### `_removeSinks()`

移除数据接收器。

##### `_initGesture()`

初始化手势绑定。

##### `Create()`

创建UI（系统回调）。

##### `Destroy()`

销毁UI（系统回调）。

##### `remove()`

移除UI。

##### `_performBackPressed(*_)`

执行返回按钮按下操作。

##### `onCreate()`

创建回调（可重写）。

##### `onBackPressed()`

返回按钮按下回调（可重写）。

- **返回值**: 布尔值，`True` 表示阻止默认返回行为

##### `onDestroy()`

销毁回调（可重写）。

## 函数

### `UiDef(uiDef)`

UI定义装饰器。

- **`uiDef`**: UI定义
- **返回值**: 装饰器函数

### `AutoCreate(cls)`

自动创建装饰器。

- **`cls`**: 类
- **返回值**: 装饰后的类

### `Screen(cls)`

屏幕装饰器。

- **`cls`**: 类
- **返回值**: 装饰后的类

### `Hud(cls)`

HUD装饰器。

- **`cls`**: 类
- **返回值**: 装饰后的类

### `Sink(method)`

数据接收器装饰器。

- **`method`**: 方法
- **返回值**: 装饰后的方法

### `signal(defaultValue=None, updater=None)`

创建响应式信号。

- **`defaultValue`**: 默认值
- **`updater`**: 更新函数，接受新值和旧值，返回更新后的值
- **返回值**: 元组 `(getter, setter)`

### `reactive(obj)`

创建响应式对象（仅用于新式类，继承自 `object`）。

- **`obj`**: 对象
- **返回值**: 元组 `(getter, setter)`

## 使用示例

### 1. 基本UI定义

```python
from ..architect.ui.client import UiDef, AutoCreate, Screen, UiSubsystem

@UiDef({
    "namespace": "my_game",
    "controls": [
        {
            "type": "panel",
            "name": "main_panel",
            "position": [0, 0, 100, 100],
            "children": [
                {
                    "type": "label",
                    "name": "title_label",
                    "text": "我的游戏",
                    "position": [10, 10, 80, 20]
                },
                {
                    "type": "button",
                    "name": "start_button",
                    "text": "开始游戏",
                    "position": [10, 40, 80, 30]
                }
            ]
        }
    ]
})
@AutoCreate
@Screen
class MainMenuScreen(UiSubsystem):
    def onCreate(self):
        """UI创建时调用"""
        print("主菜单屏幕已创建")
        
        # 获取控件
        title_label = self.find("/main_panel/title_label")
        start_button = self.find("/main_panel/start_button")
        
        # 设置按钮点击事件
        start_button.SetTouchEventCallback(self.on_start_button_click)
    
    def on_start_button_click(self, args):
        """开始按钮点击事件"""
        print("开始游戏按钮被点击")
        
        # 切换到游戏屏幕
        self.switch_to_game_screen()
    
    def onBackPressed(self):
        """返回按钮按下事件"""
        print("主菜单返回按钮按下")
        
        # 阻止默认返回行为，显示确认对话框
        self.show_exit_confirmation()
        return True  # 阻止默认返回行为
    
    def onDestroy(self):
        """UI销毁时调用"""
        print("主菜单屏幕已销毁")
    
    def switch_to_game_screen(self):
        """切换到游戏屏幕"""
        # 移除当前屏幕
        self.remove()
        
        # 创建游戏屏幕
        from .game_screen import GameScreen
        GameScreen.pushScreen()
```

### 2. 响应式数据绑定

```python
from ..architect.ui.client import signal, reactive, Sink, UiSubsystem
from ..architect.ui import UiDef, AutoCreate, Hud

# 创建响应式信号
player_health, set_player_health = signal(100)
player_name, set_player_name = signal("玩家1")
player_level, set_player_level = signal(1)

@UiDef({
    "namespace": "my_game",
    "controls": [
        {
            "type": "panel",
            "name": "hud_panel",
            "position": [10, 10, 200, 100],
            "children": [
                {
                    "type": "label",
                    "name": "health_label",
                    "text": "生命值: 100",
                    "position": [0, 0, 150, 20]
                },
                {
                    "type": "label",
                    "name": "name_label",
                    "text": "玩家1",
                    "position": [0, 25, 150, 20]
                },
                {
                    "type": "label",
                    "name": "level_label",
                    "text": "等级: 1",
                    "position": [0, 50, 150, 20]
                }
            ]
        }
    ]
})
@AutoCreate
@Hud
class GameHUD(UiSubsystem):
    def __init__(self, engine, system, params):
        super().__init__(engine, system, params)
        
        # 创建响应式对象
        self.player_stats = PlayerStats()
    
    def onCreate(self):
        """UI创建时调用"""
        print("游戏HUD已创建")
        
        # 初始化数据接收器
        self.update_hud()
    
    @Sink
    def update_hud(self):
        """更新HUD（数据接收器）"""
        # 获取控件
        health_label = self.find("/hud_panel/health_label")
        name_label = self.find("/hud_panel/name_label")
        level_label = self.find("/hud_panel/level_label")
        
        # 更新显示（使用响应式信号）
        health_label.SetText(f"生命值: {player_health()}")
        name_label.SetText(f"名称: {player_name()}")
        level_label.SetText(f"等级: {player_level()}")
        
        # 使用响应式对象
        health_label.SetText(f"生命值: {self.player_stats.health}")
        name_label.SetText(f"名称: {self.player_stats.name}")
        level_label.SetText(f"等级: {self.player_stats.level}")
    
    def take_damage(self, damage):
        """受到伤害"""
        new_health = max(0, player_health() - damage)
        set_player_health(new_health)
        
        # 响应式信号会自动触发 update_hud
    
    def level_up(self):
        """升级"""
        set_player_level(player_level() + 1)
        
        # 恢复生命值
        set_player_health(100 + (player_level() - 1) * 20)

class PlayerStats:
    """响应式玩家状态"""
    def __init__(self):
        # 创建响应式属性
        self._health_getter, self._health_setter = reactive(self)
        self._name_getter, self._name_setter = reactive(self)
        self._level_getter, self._level_setter = reactive(self)
        
        # 初始化值
        self._health = 100
        self._name = "玩家1"
        self._level = 1
    
    @property
    def health(self):
        return self._health_getter()
    
    @health.setter
    def health(self, value):
        self._health_setter(value)
        self._health = value
    
    @property
    def name(self):
        return self._name_getter()
    
    @name.setter
    def name(self, value):
        self._name_setter(value)
        self._name = value
    
    @property
    def level(self):
        return self._level_getter()
    
    @level.setter
    def level(self, value):
        self._level_setter(value)
        self._level = value
```

### 3. 带更新器的响应式信号

```python
from ..architect.ui.client import signal

# 创建带更新器的信号
def health_updater(new_value, old_value):
    """生命值更新器"""
    # 确保生命值在0-200之间
    new_value = max(0, min(200, new_value))
    
    # 记录变化
    print(f"生命值从 {old_value} 变为 {new_value}")
    
    # 检查死亡
    if new_value <= 0:
        print("玩家死亡！")
    
    return new_value

# 创建信号
player_health, set_player_health = signal(100, health_updater)

# 使用信号
print(f"当前生命值: {player_health()}")  # 100

# 设置新值（会调用更新器）
set_player_health(150)  # 输出: "生命值从 100 变为 150"
print(f"当前生命值: {player_health()}")  # 150

# 尝试设置超出范围的值
set_player_health(250)  # 输出: "生命值从 150 变为 200"（被限制为200）
print(f"当前生命值: {player_health()}")  # 200

# 尝试设置负值
set_player_health(-50)  # 输出: "生命值从 200 变为 0" 和 "玩家死亡！"
print(f"当前生命值: {player_health()}")  # 0
```

### 4. 复杂UI管理系统

```python
from ..architect.ui.client import UiSubsystem, UiDef, AutoCreate, Screen
from ..architect.event import Event

class UIManager:
    def __init__(self):
        self.screens = {}
        self.current_screen = None
        self.screen_stack = []
        
        # 注册事件监听器
        Event.on("ui_screen_change", self.on_screen_change)
        Event.on("ui_screen_push", self.on_screen_push)
        Event.on("ui_screen_pop", self.on_screen_pop)
    
    def register_screen(self, screen_class, screen_id):
        """注册屏幕"""
        self.screens[screen_id] = screen_class
        print(f"注册屏幕: {screen_id} -> {screen_class.__name__}")
    
    def show_screen(self, screen_id, params=None):
        """显示屏幕"""
        if screen_id not in self.screens:
            print(f"错误: 未注册的屏幕 {screen_id}")
            return
        
        # 隐藏当前屏幕
        if self.current_screen:
            self.current_screen.remove()
        
        # 创建新屏幕
        screen_class = self.screens[screen_id]
        screen = screen_class.pushScreen(**(params or {}))
        
        # 更新当前屏幕
        self.current_screen = screen
        
        # 触发事件
        Event.emit("ui_screen_change", screen_id, params)
        
        print(f"显示屏幕: {screen_id}")
    
    def push_screen(self, screen_id, params=None):
        """推送屏幕（压栈）"""
        if screen_id not in self.screens:
            print(f"错误: 未注册的屏幕 {screen_id}")
            return
        
        # 将当前屏幕压栈
        if self.current_screen:
            self.screen_stack.append(self.current_screen)
        
        # 创建新屏幕
        screen_class = self.screens[screen_id]
        screen = screen_class.pushScreen(**(params or {}))
        
        # 更新当前屏幕
        self.current_screen = screen
        
        # 触发事件
        Event.emit("ui_screen_push", screen_id, params)
        
        print(f"推送屏幕: {screen_id}, 栈大小: {len(self.screen_stack)}")
    
    def pop_screen(self):
        """弹出屏幕"""
        if not self.screen_stack:
            print("错误: 屏幕栈为空")
            return
        
        # 移除当前屏幕
        if self.current_screen:
            self.current_screen.remove()
        
        # 弹出上一个屏幕
        prev_screen = self.screen_stack.pop()
        
        # 恢复上一个屏幕
        # 注意: 这里需要根据具体实现调整
        # 可能需要重新创建屏幕而不是直接显示
        
        # 触发事件
        Event.emit("ui_screen_pop")
        
        print(f"弹出屏幕, 栈大小: {len(self.screen_stack)}")
    
    def on_screen_change(self, screen_id, params):
        """屏幕切换事件处理"""
        print(f"屏幕切换: {screen_id}")
    
    def on_screen_push(self, screen_id, params):
        """屏幕推送事件处理"""
        print(f"屏幕推送: {screen_id}")
    
    def on_screen_pop(self):
        """屏幕弹出事件处理"""
        print("屏幕弹出")

# 定义多个屏幕
@UiDef({"namespace": "my_game", "controls": [...]})
@AutoCreate
@Screen
class MainMenuScreen(UiSubsystem):
    pass

@UiDef({"namespace": "my_game", "controls": [...]})
@AutoCreate
@Screen
class GameScreen(UiSubsystem):
    pass

@UiDef({"namespace": "my_game", "controls": [...]})
@AutoCreate
@Screen
class InventoryScreen(UiSubsystem):
    pass

@UiDef({"namespace": "my_game", "controls": [...]})
@AutoCreate
@Screen
class SettingsScreen(UiSubsystem):
    pass

# 使用UI管理器
ui_manager = UIManager()

# 注册屏幕
ui_manager.register_screen(MainMenuScreen, "main_menu")
ui_manager.register_screen(GameScreen, "game")
ui_manager.register_screen(InventoryScreen, "inventory")
ui_manager.register_screen(SettingsScreen, "settings")

# 显示主菜单
ui_manager.show_screen("main_menu")

# 推送游戏屏幕
ui_manager.push_screen("game")

# 推送库存屏幕
ui_manager.push_screen("inventory")

# 弹出库存屏幕（返回游戏屏幕）
ui_manager.pop_screen()

# 弹出游戏屏幕（返回主菜单）
ui_manager.pop_screen()
```

### 5. 手势绑定

```python
from ..architect.ui.client import UiSubsystem, UiDef, AutoCreate, Hud
from ..architect.ui.gesture import GestureBinder

@UiDef({
    "namespace": "my_game",
    "controls": [
        {
            "type": "panel",
            "name": "gesture_panel",
            "position": [0, 0, 100, 100],
            "children": [
                {
                    "type": "image",
                    "name": "gesture_area",
                    "position": [10, 10,