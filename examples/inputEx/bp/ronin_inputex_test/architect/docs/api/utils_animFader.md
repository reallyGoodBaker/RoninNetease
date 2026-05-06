# 动画淡入淡出工具 (AnimFader) API

`architect.utils.animFader` 模块提供了动画淡入淡出功能，用于创建平滑的过渡效果。

## 依赖

- `..subsystem.ClientSubsystem`, `SubsystemClient` - 子系统客户端
- `..event.EventListener` - 事件监听器
- `..level.client.LevelClient`, `compClient` - 客户端层级组件

## 类

### `AnimFader`

动画淡入淡出类，使用 `@SubsystemClient` 装饰器标记为客户端子系统。

#### 装饰器

##### `@SubsystemClient`

将类标记为客户端子系统，使其能够集成到架构的子系统管理器中。

## 使用示例

### 1. 基本动画淡入淡出

```python
from ..architect.utils.animFader import AnimFader
from ..architect.subsystem import SubsystemManager

class FadeAnimation:
    def __init__(self):
        # 获取AnimFader子系统实例
        self.fader = SubsystemManager.getInstance().getSubsystem(AnimFader)
        
        # 动画状态
        self.current_value = 0.0
        self.target_value = 1.0
        self.duration = 1.0  # 1秒
        self.elapsed_time = 0.0
        self.is_animating = False
    
    def start_fade_in(self, duration=1.0):
        """开始淡入动画"""
        self.current_value = 0.0
        self.target_value = 1.0
        self.duration = duration
        self.elapsed_time = 0.0
        self.is_animating = True
        
        print(f"开始淡入动画，持续时间: {duration}秒")
    
    def start_fade_out(self, duration=1.0):
        """开始淡出动画"""
        self.current_value = 1.0
        self.target_value = 0.0
        self.duration = duration
        self.elapsed_time = 0.0
        self.is_animating = True
        
        print(f"开始淡出动画，持续时间: {duration}秒")
    
    def update(self, delta_time):
        """更新动画"""
        if not self.is_animating:
            return
        
        # 更新经过的时间
        self.elapsed_time += delta_time
        
        # 计算进度（0到1之间）
        progress = min(1.0, self.elapsed_time / self.duration)
        
        # 使用缓动函数计算当前值
        self.current_value = self.ease_in_out(progress, self.current_value, self.target_value)
        
        # 检查动画是否完成
        if progress >= 1.0:
            self.is_animating = False
            self.current_value = self.target_value
            print("动画完成")
    
    def ease_in_out(self, t, start, end):
        """缓入缓出函数"""
        # 简单的线性插值
        return start + (end - start) * t
    
    def get_current_value(self):
        """获取当前值"""
        return self.current_value
    
    def is_complete(self):
        """检查动画是否完成"""
        return not self.is_animating and abs(self.current_value - self.target_value) < 0.001
```

### 2. UI元素淡入淡出

```python
from ..architect.utils.animFader import AnimFader
from ..architect.subsystem import SubsystemManager
from ..architect.ui.client import UiSubsystem

class UIFadeManager:
    def __init__(self):
        self.fader = SubsystemManager.getInstance().getSubsystem(AnimFader)
        self.ui_elements = {}
        self.active_fades = []
    
    def fade_in_element(self, element_id, ui_element, duration=0.5):
        """淡入UI元素"""
        # 确保元素可见
        ui_element.visible = True
        
        # 创建淡入动画
        fade_animation = {
            'element_id': element_id,
            'ui_element': ui_element,
            'start_alpha': 0.0,
            'target_alpha': 1.0,
            'duration': duration,
            'elapsed_time': 0.0,
            'is_active': True
        }
        
        # 设置初始透明度
        ui_element.alpha = 0.0
        
        # 添加到活动淡入淡出列表
        self.active_fades.append(fade_animation)
        
        # 注册UI元素
        self.ui_elements[element_id] = ui_element
        
        print(f"开始淡入UI元素: {element_id}, 持续时间: {duration}秒")
    
    def fade_out_element(self, element_id, duration=0.5, hide_on_complete=True):
        """淡出UI元素"""
        if element_id not in self.ui_elements:
            print(f"错误: UI元素未找到: {element_id}")
            return
        
        ui_element = self.ui_elements[element_id]
        
        # 创建淡出动画
        fade_animation = {
            'element_id': element_id,
            'ui_element': ui_element,
            'start_alpha': ui_element.alpha,
            'target_alpha': 0.0,
            'duration': duration,
            'elapsed_time': 0.0,
            'is_active': True,
            'hide_on_complete': hide_on_complete
        }
        
        # 添加到活动淡入淡出列表
        self.active_fades.append(fade_animation)
        
        print(f"开始淡出UI元素: {element_id}, 持续时间: {duration}秒")
    
    def update_fades(self, delta_time):
        """更新所有淡入淡出动画"""
        completed_fades = []
        
        for i, fade in enumerate(self.active_fades):
            if not fade['is_active']:
                continue
            
            # 更新经过的时间
            fade['elapsed_time'] += delta_time
            
            # 计算进度
            progress = min(1.0, fade['elapsed_time'] / fade['duration'])
            
            # 计算当前透明度
            current_alpha = fade['start_alpha'] + (fade['target_alpha'] - fade['start_alpha']) * progress
            
            # 更新UI元素透明度
            fade['ui_element'].alpha = current_alpha
            
            # 检查动画是否完成
            if progress >= 1.0:
                fade['is_active'] = False
                
                # 如果淡出完成且需要隐藏元素
                if fade.get('hide_on_complete', False) and fade['target_alpha'] == 0.0:
                    fade['ui_element'].visible = False
                
                completed_fades.append(i)
                
                print(f"淡入淡出动画完成: {fade['element_id']}")
        
        # 移除已完成的动画
        for i in reversed(completed_fades):
            self.active_fades.pop(i)
    
    def cancel_fade(self, element_id):
        """取消淡入淡出动画"""
        for i, fade in enumerate(self.active_fades):
            if fade['element_id'] == element_id:
                self.active_fades.pop(i)
                print(f"取消淡入淡出动画: {element_id}")
                return True
        
        return False
    
    def is_element_fading(self, element_id):
        """检查元素是否正在淡入淡出"""
        for fade in self.active_fades:
            if fade['element_id'] == element_id and fade['is_active']:
                return True
        
        return False
    
    def get_element_alpha(self, element_id):
        """获取元素透明度"""
        if element_id in self.ui_elements:
            return self.ui_elements[element_id].alpha
        return 0.0
    
    def set_element_alpha_immediate(self, element_id, alpha):
        """立即设置元素透明度"""
        if element_id in self.ui_elements:
            self.ui_elements[element_id].alpha = alpha
            
            # 取消该元素的任何活动淡入淡出
            self.cancel_fade(element_id)
            
            # 如果透明度为0，隐藏元素
            if alpha == 0.0:
                self.ui_elements[element_id].visible = False
            else:
                self.ui_elements[element_id].visible = True
```

### 3. 屏幕过渡效果

```python
from ..architect.utils.animFader import AnimFader
from ..architect.subsystem import SubsystemManager
import time

class ScreenTransition:
    def __init__(self):
        self.fader = SubsystemManager.getInstance().getSubsystem(AnimFader)
        self.transition_type = "fade"  # fade, slide, scale, etc.
        self.transition_duration = 0.5
        self.is_transitioning = False
        self.transition_start_time = 0
        self.current_screen = None
        self.next_screen = None
        self.on_complete_callback = None
    
    def fade_to_screen(self, next_screen, duration=0.5, callback=None):
        """淡入淡出到下一个屏幕"""
        if self.is_transitioning:
            print("警告: 已经在过渡中")
            return False
        
        self.transition_type = "fade"
        self.transition_duration = duration
        self.next_screen = next_screen
        self.on_complete_callback = callback
        
        # 开始过渡
        self.start_transition()
        
        return True
    
    def slide_to_screen(self, next_screen, direction="right", duration=0.5, callback=None):
        """滑动到下一个屏幕"""
        if self.is_transitioning:
            print("警告: 已经在过渡中")
            return False
        
        self.transition_type = f"slide_{direction}"
        self.transition_duration = duration
        self.next_screen = next_screen
        self.on_complete_callback = callback
        
        # 开始过渡
        self.start_transition()
        
        return True
    
    def start_transition(self):
        """开始过渡"""
        self.is_transitioning = True
        self.transition_start_time = time.time()
        
        print(f"开始屏幕过渡: {self.transition_type}, 持续时间: {self.transition_duration}秒")
        
        # 设置初始状态
        self.setup_initial_state()
    
    def setup_initial_state(self):
        """设置初始状态"""
        if self.transition_type == "fade":
            # 淡入淡出过渡
            if self.current_screen:
                self.current_screen.alpha = 1.0
                self.current_screen.visible = True
            
            if self.next_screen:
                self.next_screen.alpha = 0.0
                self.next_screen.visible = True
        
        elif self.transition_type.startswith("slide_"):
            # 滑动过渡
            direction = self.transition_type.split("_")[1]
            
            if self.current_screen:
                self.current_screen.position = [0, 0]
                self.current_screen.visible = True
            
            if self.next_screen:
                # 根据方向设置初始位置
                if direction == "right":
                    self.next_screen.position = [100, 0]  # 屏幕右侧
                elif direction == "left":
                    self.next_screen.position = [-100, 0]  # 屏幕左侧
                elif direction == "up":
                    self.next_screen.position = [0, 100]  # 屏幕上方
                elif direction == "down":
                    self.next_screen.position = [0, -100]  # 屏幕下方
                
                self.next_screen.visible = True
    
    def update_transition(self):
        """更新过渡"""
        if not self.is_transitioning:
            return
        
        # 计算进度
        current_time = time.time()
        elapsed = current_time - self.transition_start_time
        progress = min(1.0, elapsed / self.transition_duration)
        
        # 应用过渡效果
        self.apply_transition(progress)
        
        # 检查过渡是否完成
        if progress >= 1.0:
            self.complete_transition()
    
    def apply_transition(self, progress):
        """应用过渡效果"""
        if self.transition_type == "fade":
            # 淡入淡出效果
            if self.current_screen:
                self.current_screen.alpha = 1.0 - progress
            
            if self.next_screen:
                self.next_screen.alpha = progress
        
        elif self.transition_type.startswith("slide_"):
            # 滑动效果
            direction = self.transition_type.split("_")[1]
            
            if self.current_screen:
                # 当前屏幕移出
                if direction == "right":
                    self.current_screen.position = [-100 * progress, 0]
                elif direction == "left":
                    self.current_screen.position = [100 * progress, 0]
                elif direction == "up":
                    self.current_screen.position = [0, -100 * progress]
                elif direction == "down":
                    self.current_screen.position = [0, 100 * progress]
            
            if self.next_screen:
                # 下一个屏幕移入
                if direction == "right":
                    self.next_screen.position = [100 * (1 - progress), 0]
                elif direction == "left":
                    self.next_screen.position = [-100 * (1 - progress), 0]
                elif direction == "up":
                    self.next_screen.position = [0, 100 * (1 - progress)]
                elif direction == "down":
                    self.next_screen.position = [0, -100 * (1 - progress)]
    
    def complete_transition(self):
        """完成过渡"""
        self.is_transitioning = False
        
        # 隐藏当前屏幕
        if self.current_screen:
            self.current_screen.visible = False
        
        # 显示下一个屏幕
        if self.next_screen:
            # 重置位置和透明度
            self.next_screen.position = [0, 0]
            self.next_screen.alpha = 1.0
            self.next_screen.visible = True
        
        # 更新当前屏幕
        self.current_screen = self.next_screen
        self.next_screen = None
        
        print("屏幕过渡完成")
        
        # 调用完成回调
        if self.on_complete_callback:
            self.on_complete_callback()
    
    def cancel_transition(self):
        """取消过渡"""
        if not self.is_transitioning:
            return
        
        self.is_transitioning = False
        
        # 重置状态
        if self.current_screen:
            self.current_screen.position = [0, 0]
            self.current_screen.alpha = 1.0
            self.current_screen.visible = True
        
        if self.next_screen:
            self.next_screen.visible = False
        
        self.next_screen = None
        
        print("屏幕过渡已取消")
```

### 4. 复杂动画序列

```python
from ..architect.utils.animFader import AnimFader
from ..architect.subsystem import SubsystemManager
import time

class AnimationSequence:
    def __init__(self):
        self.fader = SubsystemManager.getInstance().getSubsystem(AnimFader)
        self.animations = []
        self.current_animation_index = -1
        self.is_playing = False
        self.loop = False
        self.speed = 1.0
        self.on_complete = None
        self.on_each_complete = None
    
    def add_animation(self, animation):
        """添加动画到序列"""
        self.animations.append(animation)
        return len(self.animations) - 1
    
    def create_fade_animation(self, target, start_value, end_value, duration, easing="linear"):
        """创建淡入淡出动画"""
        animation = {
            'type': 'fade',
            'target': target,
            'start_value': start_value,
            'end_value': end_value,
            'duration': duration,
            'elapsed_time': 0.0,
            'easing': easing,
            'is_active': False,
            'is_complete': False
        }
        
        return animation
    
    def create_move_animation(self, target, start_pos, end_pos, duration, easing="linear"):
        """创建移动动画"""
        animation = {
            'type': 'move',
            'target': target,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'duration': duration,
            'elapsed_time': 0.0,
            'easing': easing,
            'is_active': False,
            'is_complete': False
        }
        
        return animation
    
    def create_scale_animation(self, target, start_scale, end_scale, duration, easing="linear"):
        """创建缩放动画"""
        animation = {
            'type': 'scale',
            'target': target,
            'start_scale': start_scale,
            'end_scale': end_scale,
            'duration': duration,
            'elapsed_time': 0.0,
            'easing': easing,
            'is_active': False,
            'is_complete': False
        }
        
        return animation
    
    def create_rotate_animation(self, target, start_angle, end_angle, duration, easing="linear"):
        """创建旋转动画"""
        animation = {
            'type': 'rotate',
            'target': target,
            'start_angle': start_angle,
            'end_angle': end_angle,
            'duration': duration,
            'elapsed_time': 0.0,
            'easing': easing,
            'is_active': False,
            'is_complete': False
        }
        
        return animation
    
    def play(self):
        """播放动画序列"""
        if not self.animations:
            print("错误: 没有动画可播放")
            return
        
        self.is_playing = True
        self.current_animation_index = 0
        
        # 激活第一个动画
        if self.current_animation_index < len(self.animations):
            self.animations[self.current_animation_index]['is_active'] = True
        
        print(f"开始播放动画序列，共 {len(self.animations)} 个动画")
    
    def stop(self):
        """停止动画序列"""
        self.is_playing = False
        
        # 停用所有动画
        for animation in self.animations:
            animation['is_active'] = False
            animation['is_complete'] = False
        
        self.current_animation_index =