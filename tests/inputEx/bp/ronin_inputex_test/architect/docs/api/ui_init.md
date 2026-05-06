# UI 模块 (UI) API

`architect.ui` 模块提供了用户界面相关的功能，包括UI子系统、手势识别和响应式UI组件。

## 模块结构

`architect.ui` 模块包含以下子模块：

- `architect.ui.client` - 客户端UI子系统
- `architect.ui.gesture` - 手势识别

## 导入的符号

从 `architect.ui.client` 模块导入以下符号：

### `UiSubsystem`

UI子系统类，用于管理UI组件和界面。

### `Sink`

数据接收器类，用于处理UI数据流。

### `AutoCreate`

自动创建装饰器，用于自动创建UI组件。

### `UiDef`

UI定义类，用于定义UI结构和布局。

### `signal`

信号函数，用于创建响应式数据信号。

### `reactive`

响应式装饰器，用于创建响应式属性。

### `Screen`

屏幕类，用于管理UI屏幕和页面。

从 `architect.ui.gesture` 模块导入以下符号：

### `Gesture`

手势识别类，用于识别和处理用户手势。

## 使用示例

### 1. 基本导入

```python
from ..architect.ui import (
    UiSubsystem, Sink, AutoCreate, UiDef, 
    signal, reactive, Screen, Gesture
)

# 创建UI子系统
ui_system = UiSubsystem()

# 创建手势识别器
gesture_detector = Gesture()

# 创建响应式信号
player_health = signal(100)
player_name = signal("Player1")

# 创建响应式属性
class PlayerUI:
    @reactive
    def health(self):
        return player_health.value
    
    @reactive
    def name(self):
        return player_name.value

# 创建UI屏幕
main_screen = Screen("main")
```

### 2. UI子系统使用

```python
from ..architect.ui import UiSubsystem, UiDef, AutoCreate

class GameUI:
    def __init__(self):
        self.ui_system = UiSubsystem()
        self.setup_ui()
    
    def setup_ui(self):
        """设置游戏UI"""
        # 定义主界面
        main_ui = UiDef(
            name="main_interface",
            components=[
                {"type": "panel", "id": "main_panel", "position": [0, 0, 100, 100]},
                {"type": "label", "id": "health_label", "text": "生命值: 100", "position": [10, 10, 80, 20]},
                {"type": "button", "id": "attack_button", "text": "攻击", "position": [10, 40, 80, 30]},
                {"type": "button", "id": "defend_button", "text": "防御", "position": [10, 80, 80, 30]},
            ]
        )
        
        # 注册UI定义
        self.ui_system.register_ui(main_ui)
        
        # 自动创建UI组件
        @AutoCreate("main_interface")
        def create_main_ui():
            return main_ui
        
        # 显示UI
        self.ui_system.show("main_interface")
    
    def update_health(self, new_health):
        """更新生命值显示"""
        health_label = self.ui_system.get_component("health_label")
        if health_label:
            health_label.text = f"生命值: {new_health}"
    
    def on_attack_click(self):
        """攻击按钮点击事件"""
        print("攻击按钮被点击")
        # 执行攻击逻辑
        self.perform_attack()
    
    def on_defend_click(self):
        """防御按钮点击事件"""
        print("防御按钮被点击")
        # 执行防御逻辑
        self.perform_defend()
```

### 3. 响应式UI

```python
from ..architect.ui import signal, reactive, Sink

class ReactiveGameUI:
    def __init__(self):
        # 创建响应式信号
        self.player_health = signal(100)
        self.player_mana = signal(50)
        self.player_level = signal(1)
        self.player_experience = signal(0)
        
        # 创建数据接收器
        self.health_sink = Sink()
        self.mana_sink = Sink()
        
        # 设置响应式更新
        self.setup_reactive_updates()
    
    def setup_reactive_updates(self):
        """设置响应式更新"""
        # 当生命值变化时更新UI
        self.player_health.subscribe(lambda value: self.update_health_display(value))
        
        # 当魔法值变化时更新UI
        self.player_mana.subscribe(lambda value: self.update_mana_display(value))
        
        # 当等级变化时更新UI
        self.player_level.subscribe(lambda value: self.update_level_display(value))
    
    @reactive
    def health_percentage(self):
        """计算生命值百分比（响应式属性）"""
        max_health = 100 + (self.player_level.value - 1) * 20
        return (self.player_health.value / max_health) * 100
    
    @reactive
    def mana_percentage(self):
        """计算魔法值百分比（响应式属性）"""
        max_mana = 50 + (self.player_level.value - 1) * 10
        return (self.player_mana.value / max_mana) * 100
    
    @reactive
    def experience_to_next_level(self):
        """计算升级所需经验（响应式属性）"""
        current_level = self.player_level.value
        return current_level * 100
    
    @reactive
    def experience_percentage(self):
        """计算经验值百分比（响应式属性）"""
        needed = self.experience_to_next_level
        if needed == 0:
            return 100
        return (self.player_experience.value / needed) * 100
    
    def update_health_display(self, health):
        """更新生命值显示"""
        print(f"生命值更新: {health}")
        # 更新UI组件
        health_bar = self.get_ui_component("health_bar")
        if health_bar:
            health_bar.value = self.health_percentage
    
    def update_mana_display(self, mana):
        """更新魔法值显示"""
        print(f"魔法值更新: {mana}")
        # 更新UI组件
        mana_bar = self.get_ui_component("mana_bar")
        if mana_bar:
            mana_bar.value = self.mana_percentage
    
    def update_level_display(self, level):
        """更新等级显示"""
        print(f"等级更新: {level}")
        # 更新UI组件
        level_label = self.get_ui_component("level_label")
        if level_label:
            level_label.text = f"等级: {level}"
        
        # 更新经验条
        exp_bar = self.get_ui_component("exp_bar")
        if exp_bar:
            exp_bar.value = self.experience_percentage
    
    def take_damage(self, damage):
        """受到伤害"""
        new_health = max(0, self.player_health.value - damage)
        self.player_health.value = new_health
        
        if new_health <= 0:
            self.on_player_death()
    
    def use_mana(self, amount):
        """使用魔法值"""
        new_mana = max(0, self.player_mana.value - amount)
        self.player_mana.value = new_mana
    
    def gain_experience(self, amount):
        """获得经验值"""
        self.player_experience.value += amount
        
        # 检查是否升级
        while self.player_experience.value >= self.experience_to_next_level:
            self.level_up()
    
    def level_up(self):
        """升级"""
        # 扣除所需经验
        needed = self.experience_to_next_level
        self.player_experience.value -= needed
        
        # 增加等级
        self.player_level.value += 1
        
        # 恢复生命值和魔法值
        self.player_health.value = 100 + (self.player_level.value - 1) * 20
        self.player_mana.value = 50 + (self.player_level.value - 1) * 10
        
        print(f"恭喜升级！当前等级: {self.player_level.value}")
    
    def on_player_death(self):
        """玩家死亡"""
        print("玩家死亡！")
        # 显示死亡界面
        self.show_death_screen()
```

### 4. 手势识别

```python
from ..architect.ui import Gesture
import time

class GameGestureHandler:
    def __init__(self):
        self.gesture = Gesture()
        self.setup_gesture_handlers()
        self.last_tap_time = 0
        self.tap_count = 0
    
    def setup_gesture_handlers(self):
        """设置手势处理器"""
        # 点击手势
        self.gesture.on_tap(self.on_tap)
        
        # 双击手势
        self.gesture.on_double_tap(self.on_double_tap)
        
        # 长按手势
        self.gesture.on_long_press(self.on_long_press)
        
        # 滑动手势
        self.gesture.on_swipe(self.on_swipe)
        
        # 拖动手势
        self.gesture.on_drag(self.on_drag)
        
        # 缩放手势
        self.gesture.on_pinch(self.on_pinch)
    
    def on_tap(self, position):
        """点击事件处理"""
        current_time = time.time()
        
        # 检查是否为双击的一部分
        if current_time - self.last_tap_time < 0.3:  # 300ms内
            self.tap_count += 1
        else:
            self.tap_count = 1
        
        self.last_tap_time = current_time
        
        print(f"点击位置: {position}")
        print(f"点击次数: {self.tap_count}")
        
        # 检查点击的UI元素
        ui_element = self.get_ui_element_at_position(position)
        if ui_element:
            ui_element.on_click()
    
    def on_double_tap(self, position):
        """双击事件处理"""
        print(f"双击位置: {position}")
        
        # 双击通常用于放大或特殊操作
        if self.is_in_game_world(position):
            self.zoom_at_position(position)
        else:
            # 双击UI元素
            ui_element = self.get_ui_element_at_position(position)
            if ui_element:
                ui_element.on_double_click()
    
    def on_long_press(self, position, duration):
        """长按事件处理"""
        print(f"长按位置: {position}, 持续时间: {duration:.2f}秒")
        
        # 长按通常用于显示上下文菜单或拖拽开始
        if duration > 1.0:  # 长按超过1秒
            self.show_context_menu(position)
        else:
            self.start_drag(position)
    
    def on_swipe(self, start_position, end_position, velocity):
        """滑动手势处理"""
        print(f"滑动: 从 {start_position} 到 {end_position}, 速度: {velocity}")
        
        # 计算滑动方向
        dx = end_position[0] - start_position[0]
        dy = end_position[1] - start_position[1]
        
        # 确定滑动方向
        if abs(dx) > abs(dy):
            # 水平滑动
            if dx > 0:
                print("向右滑动")
                self.swipe_right()
            else:
                print("向左滑动")
                self.swipe_left()
        else:
            # 垂直滑动
            if dy > 0:
                print("向下滑动")
                self.swipe_down()
            else:
                print("向上滑动")
                self.swipe_up()
    
    def on_drag(self, start_position, current_position, delta):
        """拖动手势处理"""
        # 拖动通常用于移动对象或滚动内容
        print(f"拖动: 当前位置 {current_position}, 增量 {delta}")
        
        # 检查是否在拖动UI元素
        dragged_element = self.get_dragged_element()
        if dragged_element:
            dragged_element.position = current_position
        else:
            # 拖动游戏世界
            self.pan_game_world(delta)
    
    def on_pinch(self, center, scale, velocity):
        """缩放手势处理"""
        print(f"缩放: 中心点 {center}, 缩放比例 {scale:.2f}, 速度 {velocity}")
        
        # 缩放游戏视角
        self.zoom_game_camera(scale)
    
    def is_in_game_world(self, position):
        """检查位置是否在游戏世界内"""
        # 简单的边界检查
        screen_width = 800
        screen_height = 600
        ui_panel_width = 200
        
        return position[0] > ui_panel_width and position[0] < screen_width
    
    def get_ui_element_at_position(self, position):
        """获取指定位置的UI元素"""
        # 遍历所有UI元素，检查是否包含该位置
        for element in self.ui_elements:
            if element.contains_position(position):
                return element
        return None
    
    def swipe_left(self):
        """向左滑动处理"""
        # 切换到下一个标签页或向左滚动
        self.switch_to_previous_tab()
    
    def swipe_right(self):
        """向右滑动处理"""
        # 切换到上一个标签页或向右滚动
        self.switch_to_next_tab()
    
    def swipe_up(self):
        """向上滑动处理"""
        # 向上滚动或显示更多内容
        self.scroll_up()
    
    def swipe_down(self):
        """向下滑动处理"""
        # 向下滚动或隐藏内容
        self.scroll_down()
    
    def zoom_at_position(self, position):
        """在指定位置缩放"""
        # 以指定位置为中心进行缩放
        self.camera.zoom_to(position, 2.0)  # 放大2倍
    
    def show_context_menu(self, position):
        """显示上下文菜单"""
        menu_items = [
            {"text": "攻击", "action": self.attack},
            {"text": "使用物品", "action": self.use_item},
            {"text": "检查", "action": self.inspect},
            {"text": "取消", "action": self.close_menu}
        ]
        
        self.ui_system.show_context_menu(position, menu_items)
    
    def start_drag(self, position):
        """开始拖动"""
        # 查找可拖动的元素
        element = self.get_draggable_element_at_position(position)
        if element:
            self.set_dragged_element(element)
            print(f"开始拖动元素: {element.id}")
    
    def pan_game_world(self, delta):
        """平移游戏世界"""
        # 根据拖动增量移动相机
        self.camera.pan(delta[0], delta[1])
    
    def zoom_game_camera(self, scale):
        """缩放游戏相机"""
        # 根据缩放比例调整相机
        self.camera.zoom(scale)
```

### 5. 屏幕管理

```python
from ..architect.ui import Screen, UiSubsystem

class ScreenManager:
    def __init__(self):
        self.ui_system = UiSubsystem()
        self.screens = {}
        self.current_screen = None
        self.screen_history = []
        
        self.setup_screens()
    
    def setup_screens(self):
        """设置所有屏幕"""
        # 主菜单屏幕
        main_menu = Screen("main_menu")
        main_menu.add_component("title", {"type": "label", "text": "游戏主菜单", "position": [100, 50, 600, 100]})
        main_menu.add_component("start_button", {"type": "button", "text": "开始游戏", "position": [300, 200, 200, 50]})
        main_menu.add_component("options_button", {"type": "button", "text": "设置", "position": [300, 270, 200, 50]})
        main_menu.add_component("quit_button", {"type": "button", "text": "退出游戏", "position": [300, 340, 200, 50]})
        
        # 游戏屏幕
        game_screen = Screen("game")
        game_screen.add_component("health_bar", {"type": "progress", "value": 100, "position": [10, 10, 200, 20]})
        game_screen.add_component("mana_bar", {"type": "progress", "value": 50, "position": [10, 40, 200, 20]})
        game_screen.add_component("minimap", {"type": "minimap", "position": [600, 10, 150, 150]})
        game_screen.add_component("inventory_button", {"type": "button", "text": "背包", "position": [600, 170, 150, 30]})
        game_screen.add_component("skills_button", {"type": "button", "text": "技能", "position": [600, 210, 150, 30]})
        
        # 设置屏幕
        options_screen = Screen("options")
        options_screen.add_component("title", {"type": "label", "text": "游戏设置", "position": [100, 50, 600, 100]})
        options_screen.add_component("volume_slider", {"type": "slider", "value": 80, "position": [200, 200, 400, 30]})
        options_screen.add_component("back_button", {"type": "button", "text": "返回", "position": [300, 300, 200, 50]})
        
        # 注册屏幕
        self.register_screen(main_menu)
        self.register_screen(game_screen)
        self.register_screen(options_screen)
        
        # 设置屏幕切换事件
        main_menu.get_component("start_button").on_click = lambda: self.switch_to("game")
        main_menu.get_component("options_button").on_click = lambda: self.switch_to("options")
        main_menu.get_component("quit_button").on_click = self.quit_game
        
        game_screen.get_component("inventory_button").on_click = lambda: self.show