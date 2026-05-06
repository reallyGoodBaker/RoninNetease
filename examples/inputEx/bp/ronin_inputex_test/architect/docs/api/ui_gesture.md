# 手势识别 (UI Gesture) API

`architect.ui.gesture` 模块提供了UI手势识别和绑定功能，用于处理按钮和控件的触摸事件。

## 依赖

- `..annotation.AnnotationHelper` - 注解助手
- `..conf.UI_GESTURE` - 手势注解常量

## 函数

### `_btnDecoratorBuilder(type)`

内部函数，用于创建按钮装饰器构建器。

- **`type`**: 手势类型字符串
- **返回值**: 装饰器函数

## 类

### `Gesture`

手势类，提供各种手势装饰器。

#### 类属性

##### `Click`

点击手势装饰器。

##### `Move`

移动手势装饰器。

##### `MoveIn`

移入手势装饰器。

##### `MoveOut`

移出手势装饰器。

##### `Cancel`

取消手势装饰器。

##### `Down`

按下手势装饰器。

## 字典

### `GestureBinder`

手势绑定器字典，将手势类型映射到绑定函数。

- **`'click'`**: 绑定到 `SetButtonTouchUpCallback`
- **`'down'`**: 绑定到 `SetButtonTouchDownCallback`
- **`'move'`**: 绑定到 `SetButtonTouchMoveCallback`
- **`'movein'`**: 绑定到 `SetButtonTouchMoveInCallback`
- **`'moveout'`**: 绑定到 `SetButtonTouchMoveOutCallback`
- **`'cancel'`**: 绑定到 `SetButtonTouchCancelCallback`

## 使用示例

### 1. 基本手势绑定

```python
from ..architect.ui.gesture import Gesture
from ..architect.ui.client import UiSubsystem, UiDef, AutoCreate, Hud

@UiDef({
    "namespace": "my_game",
    "controls": [
        {
            "type": "panel",
            "name": "main_panel",
            "position": [0, 0, 100, 100],
            "children": [
                {
                    "type": "button",
                    "name": "attack_button",
                    "text": "攻击",
                    "position": [10, 10, 80, 30]
                },
                {
                    "type": "button",
                    "name": "defend_button",
                    "text": "防御",
                    "position": [10, 50, 80, 30]
                },
                {
                    "type": "button",
                    "name": "skill_button",
                    "text": "技能",
                    "position": [10, 90, 80, 30]
                }
            ]
        }
    ]
})
@AutoCreate
@Hud
class GameHUD(UiSubsystem):
    def onCreate(self):
        """UI创建时调用"""
        print("游戏HUD已创建")
    
    @Gesture.Click("/main_panel/attack_button")
    def on_attack_click(self, args):
        """攻击按钮点击事件"""
        print("攻击按钮被点击")
        print(f"事件参数: {args}")
        
        # 执行攻击逻辑
        self.perform_attack()
    
    @Gesture.Down("/main_panel/defend_button")
    def on_defend_down(self, args):
        """防御按钮按下事件"""
        print("防御按钮被按下")
        
        # 开始防御
        self.start_defend()
    
    @Gesture.Move("/main_panel/skill_button")
    def on_skill_move(self, args):
        """技能按钮移动事件"""
        print("技能按钮上移动")
        print(f"移动位置: {args.get('x', 0)}, {args.get('y', 0)}")
    
    @Gesture.MoveIn("/main_panel/skill_button")
    def on_skill_move_in(self, args):
        """技能按钮移入事件"""
        print("鼠标/手指移入技能按钮")
        
        # 显示技能提示
        self.show_skill_tooltip()
    
    @Gesture.MoveOut("/main_panel/skill_button")
    def on_skill_move_out(self, args):
        """技能按钮移出事件"""
        print("鼠标/手指移出技能按钮")
        
        # 隐藏技能提示
        self.hide_skill_tooltip()
    
    @Gesture.Cancel("/main_panel/skill_button")
    def on_skill_cancel(self, args):
        """技能按钮取消事件"""
        print("技能按钮触摸取消")
        
        # 取消技能释放
        self.cancel_skill()
    
    def perform_attack(self):
        """执行攻击"""
        print("执行攻击逻辑")
        # 实际攻击逻辑...
    
    def start_defend(self):
        """开始防御"""
        print("开始防御")
        # 实际防御逻辑...
    
    def show_skill_tooltip(self):
        """显示技能提示"""
        print("显示技能提示")
    
    def hide_skill_tooltip(self):
        """隐藏技能提示"""
        print("隐藏技能提示")
    
    def cancel_skill(self):
        """取消技能"""
        print("取消技能释放")
```

### 2. 复杂手势处理

```python
from ..architect.ui.gesture import Gesture
from ..architect.ui.client import UiSubsystem, UiDef, AutoCreate, Screen
import time

@UiDef({
    "namespace": "my_game",
    "controls": [
        {
            "type": "panel",
            "name": "touch_panel",
            "position": [0, 0, 100, 100],
            "children": [
                {
                    "type": "image",
                    "name": "joystick_background",
                    "position": [10, 10, 80, 80]
                },
                {
                    "type": "image",
                    "name": "joystick_thumb",
                    "position": [40, 40, 20, 20]
                }
            ]
        }
    ]
})
@AutoCreate
@Screen
class TouchControlScreen(UiSubsystem):
    def __init__(self, engine, system, params):
        super().__init__(engine, system, params)
        self.joystick_active = False
        self.joystick_center = (50, 50)  # 摇杆中心位置
        self.joystick_thumb_position = (40, 40)
        self.last_touch_time = 0
        self.touch_duration = 0
    
    def onCreate(self):
        """UI创建时调用"""
        print("触摸控制屏幕已创建")
        
        # 获取摇杆控件
        self.joystick_bg = self.find("/touch_panel/joystick_background")
        self.joystick_thumb = self.find("/touch_panel/joystick_thumb")
    
    @Gesture.Down("/touch_panel/joystick_background")
    def on_joystick_down(self, args):
        """摇杆按下事件"""
        print("摇杆被按下")
        
        self.joystick_active = True
        self.last_touch_time = time.time()
        
        # 获取触摸位置
        touch_x = args.get('touch_x', 0)
        touch_y = args.get('touch_y', 0)
        
        print(f"触摸位置: ({touch_x}, {touch_y})")
        
        # 更新摇杆拇指位置
        self.update_joystick_thumb(touch_x, touch_y)
    
    @Gesture.Move("/touch_panel/joystick_background")
    def on_joystick_move(self, args):
        """摇杆移动事件"""
        if not self.joystick_active:
            return
        
        # 获取触摸位置
        touch_x = args.get('touch_x', 0)
        touch_y = args.get('touch_y', 0)
        
        # 计算触摸持续时间
        current_time = time.time()
        self.touch_duration = current_time - self.last_touch_time
        
        print(f"摇杆移动: ({touch_x}, {touch_y}), 持续时间: {self.touch_duration:.2f}秒")
        
        # 更新摇杆拇指位置
        self.update_joystick_thumb(touch_x, touch_y)
        
        # 计算摇杆方向
        direction = self.calculate_joystick_direction(touch_x, touch_y)
        
        # 根据方向移动角色
        self.move_character(direction)
    
    @Gesture.Click("/touch_panel/joystick_background")
    def on_joystick_click(self, args):
        """摇杆点击事件"""
        print("摇杆被点击（按下并释放）")
        
        # 点击摇杆可以执行特殊动作
        if self.touch_duration < 0.5:  # 短按
            print("短按摇杆：跳跃")
            self.jump()
        else:  # 长按
            print("长按摇杆：冲刺")
            self.sprint()
        
        # 重置摇杆状态
        self.reset_joystick()
    
    @Gesture.Cancel("/touch_panel/joystick_background")
    def on_joystick_cancel(self, args):
        """摇杆取消事件"""
        print("摇杆触摸取消")
        
        # 重置摇杆状态
        self.reset_joystick()
    
    def update_joystick_thumb(self, touch_x, touch_y):
        """更新摇杆拇指位置"""
        # 计算相对于摇杆中心的位置
        center_x, center_y = self.joystick_center
        radius = 30  # 摇杆半径
        
        # 计算距离
        dx = touch_x - center_x
        dy = touch_y - center_y
        distance = (dx**2 + dy**2)**0.5
        
        # 限制在摇杆范围内
        if distance > radius:
            dx = dx * radius / distance
            dy = dy * radius / distance
        
        # 更新拇指位置
        thumb_x = center_x + dx - 10  # 减去拇指宽度的一半
        thumb_y = center_y + dy - 10  # 减去拇指高度的一半
        
        self.joystick_thumb_position = (thumb_x, thumb_y)
        
        # 更新UI
        if self.joystick_thumb:
            self.joystick_thumb.SetPosition(thumb_x, thumb_y)
    
    def calculate_joystick_direction(self, touch_x, touch_y):
        """计算摇杆方向"""
        center_x, center_y = self.joystick_center
        
        # 计算相对位置
        dx = touch_x - center_x
        dy = touch_y - center_y
        
        # 计算角度（弧度）
        import math
        angle = math.atan2(dy, dx)
        
        # 将弧度转换为角度
        angle_deg = math.degrees(angle)
        
        # 标准化角度到0-360度
        if angle_deg < 0:
            angle_deg += 360
        
        # 确定方向
        if 337.5 <= angle_deg or angle_deg < 22.5:
            direction = "right"
        elif 22.5 <= angle_deg < 67.5:
            direction = "up_right"
        elif 67.5 <= angle_deg < 112.5:
            direction = "up"
        elif 112.5 <= angle_deg < 157.5:
            direction = "up_left"
        elif 157.5 <= angle_deg < 202.5:
            direction = "left"
        elif 202.5 <= angle_deg < 247.5:
            direction = "down_left"
        elif 247.5 <= angle_deg < 292.5:
            direction = "down"
        elif 292.5 <= angle_deg < 337.5:
            direction = "down_right"
        else:
            direction = "center"
        
        # 计算强度（0-1）
        radius = 30
        distance = (dx**2 + dy**2)**0.5
        strength = min(1.0, distance / radius)
        
        return {
            "direction": direction,
            "angle": angle_deg,
            "strength": strength,
            "dx": dx,
            "dy": dy
        }
    
    def move_character(self, direction_info):
        """移动角色"""
        direction = direction_info["direction"]
        strength = direction_info["strength"]
        
        # 根据方向和强度移动角色
        speed = 5.0 * strength
        
        if direction == "right":
            print(f"向右移动，速度: {speed:.2f}")
            self.character.move_right(speed)
        elif direction == "up_right":
            print(f"向右上移动，速度: {speed:.2f}")
            self.character.move_up_right(speed)
        elif direction == "up":
            print(f"向上移动，速度: {speed:.2f}")
            self.character.move_up(speed)
        elif direction == "up_left":
            print(f"向左上移动，速度: {speed:.2f}")
            self.character.move_up_left(speed)
        elif direction == "left":
            print(f"向左移动，速度: {speed:.2f}")
            self.character.move_left(speed)
        elif direction == "down_left":
            print(f"向左下移动，速度: {speed:.2f}")
            self.character.move_down_left(speed)
        elif direction == "down":
            print(f"向下移动，速度: {speed:.2f}")
            self.character.move_down(speed)
        elif direction == "down_right":
            print(f"向右下移动，速度: {speed:.2f}")
            self.character.move_down_right(speed)
        else:
            print("停止移动")
            self.character.stop()
    
    def jump(self):
        """跳跃"""
        print("角色跳跃")
        # 实际跳跃逻辑...
    
    def sprint(self):
        """冲刺"""
        print("角色冲刺")
        # 实际冲刺逻辑...
    
    def reset_joystick(self):
        """重置摇杆"""
        self.joystick_active = False
        self.touch_duration = 0
        
        # 重置拇指位置
        center_x, center_y = self.joystick_center
        self.joystick_thumb_position = (center_x - 10, center_y - 10)
        
        # 更新UI
        if self.joystick_thumb:
            self.joystick_thumb.SetPosition(center_x - 10, center_y - 10)
        
        # 停止角色移动
        self.character.stop()
```

### 3. 手势组合和高级交互

```python
from ..architect.ui.gesture import Gesture
from ..architect.ui.client import UiSubsystem, UiDef, AutoCreate, Hud

@UiDef({
    "namespace": "my_game",
    "controls": [
        {
            "type": "panel",
            "name": "combo_panel",
            "position": [0, 0, 100, 100],
            "children": [
                {
                    "type": "button",
                    "name": "combo_button",
                    "text": "连击按钮",
                    "position": [10, 10, 80, 30]
                },
                {
                    "type": "label",
                    "name": "combo_counter",
                    "text": "连击数: 0",
                    "position": [10, 50, 80, 20]
                },
                {
                    "type": "progress",
                    "name": "combo_progress",
                    "value": 0,
                    "position": [10, 80, 80, 10]
                }
            ]
        }
    ]
})
@AutoCreate
@Hud
class ComboSystem(UiSubsystem):
    def __init__(self, engine, system, params):
        super().__init__(engine, system, params)
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 2.0  # 连击超时时间（秒）
        self.last_click_time = 0
        self.combo_active = False
    
    def onCreate(self):
        """UI创建时调用"""
        print("连击系统已创建")
        
        # 获取控件
        self.combo_counter = self.find("/combo_panel/combo_counter")
        self.combo_progress = self.find("/combo_panel/combo_progress")
        
        # 启动定时器更新连击状态
        self.start_combo_timer()
    
    @Gesture.Click("/combo_panel/combo_button")
    def on_combo_click(self, args):
        """连击按钮点击事件"""
        current_time = time.time()
        
        # 检查是否在连击时间内
        if self.combo_active and (current_time - self.last_click_time) < self.combo_timeout:
            # 增加连击数
            self.combo_count += 1
            print(f"连击成功！当前连击数: {self.combo_count}")
        else:
            # 开始新的连击
            self.combo_count = 1
            self.combo_active = True
            print("开始新连击")
        
        # 更新最后点击时间
        self.last_click_time = current_time
        
        # 重置连击计时器
        self.combo_timer = 0
        
        # 更新UI
        self.update_combo_display()
        
        # 根据连击数执行不同效果
        self.execute_combo_effect()
    
    @Gesture.Down("/combo_panel/combo_button")
    def on_combo_down(self, args):
        """连击按钮按下事件"""
        print("连击按钮按下")
        
        # 可以在这里处理长按逻辑
        # 例如：开始蓄力
    
    @Gesture.Move("/combo_panel/combo_button")
    def on_combo_move(self, args):
        """连击按钮移动事件"""
        # 可以在这里处理滑动逻辑
        # 例如：在按钮上滑动可以调整连击类型
        pass
    
    def start_combo_timer(self):
        """启动连击计时器"""
        def update_timer():
            if self.combo_active:
                self.combo_timer += 0.1  # 每0.1秒更新一次
                
                # 更新进度条
                if self.combo_progress:
                    progress_value = 100 * (1 - self.combo_timer / self.combo