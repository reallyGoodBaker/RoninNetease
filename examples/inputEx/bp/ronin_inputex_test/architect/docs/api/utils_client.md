# 客户端工具 (ClientUtils) API

`architect.utils.client` 模块提供了客户端实用工具，包括自定义音频播放功能。

## 依赖

- `..subsystem.ClientSubsystem`, `SubsystemClient` - 子系统客户端
- `..event.EventListener` - 事件监听器
- `..level.client.LevelClient`, `compClient` - 客户端层级组件

## 类

### `ClientUtilsSubsys`

客户端工具子系统类，继承自 `ClientSubsystem`，使用 `@SubsystemClient` 装饰器标记。

#### 装饰器

##### `@SubsystemClient`

将类标记为客户端子系统，使其能够集成到架构的子系统管理器中。

#### 构造函数

##### `onInit()`

初始化方法，在子系统初始化时调用。

- **功能**: 获取 `LevelClient` 实例并存储在 `self.level` 中

#### 方法

##### `playSound(ev)`

播放自定义音频事件处理器。

- **装饰器**: `@EventListener('PlayCustomAudio', isCustomEvent=True)`
- **参数**: `ev` - 事件对象，包含以下属性：
  - `entityId`: 实体ID
  - `sound`: 声音标识符
- **功能**: 在指定实体位置播放自定义音乐

##### `stopSound(ev)`

停止自定义音频事件处理器。

- **装饰器**: `@EventListener('StopCustomAudio', isCustomEvent=True)`
- **参数**: `ev` - 事件对象，包含以下属性：
  - `sound`: 声音标识符
- **功能**: 停止播放指定的自定义音乐，使用0.1秒的淡出时间

## 使用示例

### 1. 基本音频播放

```python
from ..architect.utils.client import ClientUtilsSubsys
from ..architect.subsystem import SubsystemManager
from ..architect.event import Event

class AudioManager:
    def __init__(self):
        # 获取客户端工具子系统实例
        self.client_utils = SubsystemManager.getInstance().getSubsystem(ClientUtilsSubsys)
        
        # 音频配置
        self.audio_config = {
            'background_music': 'music.background',
            'button_click': 'sound.button_click',
            'player_hurt': 'sound.player_hurt',
            'player_death': 'sound.player_death',
            'item_pickup': 'sound.item_pickup',
            'level_up': 'sound.level_up'
        }
        
        # 当前播放的音频
        self.current_audio = {}
    
    def play_background_music(self, entity_id=None):
        """播放背景音乐"""
        sound_id = self.audio_config['background_music']
        
        # 创建播放音频事件
        event_data = {
            'entityId': entity_id or 0,  # 使用0表示全局位置
            'sound': sound_id
        }
        
        # 触发事件
        Event.emit('PlayCustomAudio', event_data)
        
        # 记录当前播放的音频
        self.current_audio['background'] = sound_id
        
        print(f"播放背景音乐: {sound_id}")
    
    def stop_background_music(self):
        """停止背景音乐"""
        if 'background' in self.current_audio:
            sound_id = self.current_audio['background']
            
            # 创建停止音频事件
            event_data = {
                'sound': sound_id
            }
            
            # 触发事件
            Event.emit('StopCustomAudio', event_data)
            
            # 移除记录
            del self.current_audio['background']
            
            print(f"停止背景音乐: {sound_id}")
    
    def play_sound_effect(self, sound_name, entity_id=None):
        """播放音效"""
        if sound_name not in self.audio_config:
            print(f"错误: 未知音效: {sound_name}")
            return
        
        sound_id = self.audio_config[sound_name]
        
        # 创建播放音频事件
        event_data = {
            'entityId': entity_id or 0,
            'sound': sound_id
        }
        
        # 触发事件
        Event.emit('PlayCustomAudio', event_data)
        
        print(f"播放音效: {sound_name} -> {sound_id}")
    
    def play_button_click(self, button_name):
        """播放按钮点击音效"""
        self.play_sound_effect('button_click')
        print(f"按钮点击: {button_name}")
    
    def play_player_hurt(self, player_id):
        """播放玩家受伤音效"""
        self.play_sound_effect('player_hurt', player_id)
        print(f"玩家受伤: {player_id}")
    
    def play_player_death(self, player_id):
        """播放玩家死亡音效"""
        self.play_sound_effect('player_death', player_id)
        print(f"玩家死亡: {player_id}")
    
    def play_item_pickup(self, player_id):
        """播放物品拾取音效"""
        self.play_sound_effect('item_pickup', player_id)
        print(f"物品拾取: {player_id}")
    
    def play_level_up(self, player_id):
        """播放升级音效"""
        self.play_sound_effect('level_up', player_id)
        print(f"玩家升级: {player_id}")
    
    def stop_all_audio(self):
        """停止所有音频"""
        # 停止背景音乐
        self.stop_background_music()
        
        # 可以添加停止其他音频的逻辑
        print("停止所有音频")
```

### 2. 位置音频系统

```python
from ..architect.utils.client import ClientUtilsSubsys
from ..architect.subsystem import SubsystemManager
from ..architect.event import Event
from ..architect.math.vec3 import Vec3

class PositionalAudioSystem:
    def __init__(self):
        self.client_utils = SubsystemManager.getInstance().getSubsystem(ClientUtilsSubsys)
        self.audio_sources = {}  # 音频源字典
        self.listener_position = Vec3(0, 0, 0)  # 听者位置
        self.max_audio_distance = 50.0  # 最大可听距离
    
    def add_audio_source(self, source_id, position, sound_id, loop=False, volume=1.0):
        """添加音频源"""
        self.audio_sources[source_id] = {
            'position': Vec3(*position),
            'sound_id': sound_id,
            'loop': loop,
            'volume': volume,
            'is_playing': False,
            'distance': 0.0,
            'volume_multiplier': 1.0
        }
        
        print(f"添加音频源: {source_id}, 位置: {position}, 声音: {sound_id}")
    
    def remove_audio_source(self, source_id):
        """移除音频源"""
        if source_id in self.audio_sources:
            # 如果正在播放，先停止
            if self.audio_sources[source_id]['is_playing']:
                self.stop_audio_source(source_id)
            
            del self.audio_sources[source_id]
            print(f"移除音频源: {source_id}")
    
    def update_listener_position(self, position):
        """更新听者位置"""
        self.listener_position = Vec3(*position)
        
        # 更新所有音频源的距离和音量
        for source_id, source in self.audio_sources.items():
            if source['is_playing']:
                self.update_audio_source(source_id)
    
    def update_audio_source(self, source_id):
        """更新音频源"""
        if source_id not in self.audio_sources:
            return
        
        source = self.audio_sources[source_id]
        
        # 计算距离
        distance = source['position'].distance_to(self.listener_position)
        source['distance'] = distance
        
        # 计算音量乘数（基于距离）
        if distance <= self.max_audio_distance:
            # 线性衰减
            volume_multiplier = 1.0 - (distance / self.max_audio_distance)
            volume_multiplier = max(0.0, min(1.0, volume_multiplier))
        else:
            volume_multiplier = 0.0
        
        source['volume_multiplier'] = volume_multiplier
        
        # 如果音量乘数为0且正在播放，停止音频
        if volume_multiplier <= 0.0 and source['is_playing']:
            self.stop_audio_source(source_id)
        # 如果音量乘数大于0且未播放，开始播放
        elif volume_multiplier > 0.0 and not source['is_playing']:
            self.play_audio_source(source_id)
    
    def play_audio_source(self, source_id):
        """播放音频源"""
        if source_id not in self.audio_sources:
            return
        
        source = self.audio_sources[source_id]
        
        # 检查距离
        if source['distance'] > self.max_audio_distance:
            return
        
        # 创建播放音频事件
        event_data = {
            'entityId': 0,  # 使用0表示自定义位置
            'sound': source['sound_id'],
            'position': source['position'].to_list(),  # 添加位置信息
            'volume': source['volume'] * source['volume_multiplier']
        }
        
        # 触发事件
        Event.emit('PlayCustomAudio', event_data)
        
        source['is_playing'] = True
        print(f"播放音频源: {source_id}, 音量: {event_data['volume']:.2f}")
    
    def stop_audio_source(self, source_id):
        """停止音频源"""
        if source_id not in self.audio_sources:
            return
        
        source = self.audio_sources[source_id]
        
        # 创建停止音频事件
        event_data = {
            'sound': source['sound_id']
        }
        
        # 触发事件
        Event.emit('StopCustomAudio', event_data)
        
        source['is_playing'] = False
        print(f"停止音频源: {source_id}")
    
    def update_all_audio_sources(self):
        """更新所有音频源"""
        for source_id in self.audio_sources:
            self.update_audio_source(source_id)
    
    def set_audio_source_position(self, source_id, position):
        """设置音频源位置"""
        if source_id in self.audio_sources:
            self.audio_sources[source_id]['position'] = Vec3(*position)
            self.update_audio_source(source_id)
    
    def set_audio_source_volume(self, source_id, volume):
        """设置音频源音量"""
        if source_id in self.audio_sources:
            self.audio_sources[source_id]['volume'] = max(0.0, min(1.0, volume))
            self.update_audio_source(source_id)
    
    def set_max_audio_distance(self, distance):
        """设置最大音频距离"""
        self.max_audio_distance = max(0.0, distance)
        self.update_all_audio_sources()
    
    def get_audio_source_info(self, source_id):
        """获取音频源信息"""
        if source_id in self.audio_sources:
            source = self.audio_sources[source_id]
            return {
                'position': source['position'].to_list(),
                'sound_id': source['sound_id'],
                'is_playing': source['is_playing'],
                'distance': source['distance'],
                'volume': source['volume'],
                'volume_multiplier': source['volume_multiplier']
            }
        return None
```

### 3. 音频事件扩展

```python
from ..architect.utils.client import ClientUtilsSubsys
from ..architect.subsystem import SubsystemManager
from ..architect.event import Event, EventListener

class ExtendedAudioSystem(ClientUtilsSubsys):
    def __init__(self):
        super().__init__()
        self.audio_queue = []  # 音频队列
        self.is_playing = False
        self.current_audio = None
        self.audio_volume = 1.0
        self.master_volume = 1.0
    
    def onInit(self):
        """初始化"""
        super().onInit()
        print("扩展音频系统已初始化")
    
    @EventListener('PlayAudioQueue', isCustomEvent=True)
    def handle_play_audio_queue(self, ev):
        """处理播放音频队列事件"""
        audio_list = ev.get('audio_list', [])
        clear_queue = ev.get('clear_queue', True)
        
        if clear_queue:
            self.clear_audio_queue()
        
        for audio in audio_list:
            self.add_to_audio_queue(audio)
        
        if not self.is_playing:
            self.play_next_in_queue()
    
    @EventListener('SetAudioVolume', isCustomEvent=True)
    def handle_set_audio_volume(self, ev):
        """处理设置音频音量事件"""
        volume_type = ev.get('type', 'master')  # master, music, effects
        volume = ev.get('volume', 1.0)
        
        if volume_type == 'master':
            self.master_volume = max(0.0, min(1.0, volume))
            print(f"设置主音量: {self.master_volume:.2f}")
        elif volume_type == 'music':
            self.audio_volume = max(0.0, min(1.0, volume))
            print(f"设置音乐音量: {self.audio_volume:.2f}")
        elif volume_type == 'effects':
            # 可以添加音效音量控制
            pass
    
    @EventListener('PauseAllAudio', isCustomEvent=True)
    def handle_pause_all_audio(self, ev):
        """处理暂停所有音频事件"""
        self.pause_current_audio()
        print("暂停所有音频")
    
    @EventListener('ResumeAllAudio', isCustomEvent=True)
    def handle_resume_all_audio(self, ev):
        """处理恢复所有音频事件"""
        self.resume_current_audio()
        print("恢复所有音频")
    
    def add_to_audio_queue(self, audio_info):
        """添加到音频队列"""
        self.audio_queue.append(audio_info)
        print(f"添加到音频队列: {audio_info.get('name', '未知音频')}")
    
    def clear_audio_queue(self):
        """清空音频队列"""
        self.audio_queue.clear()
        print("清空音频队列")
    
    def play_next_in_queue(self):
        """播放队列中的下一个音频"""
        if not self.audio_queue:
            self.is_playing = False
            self.current_audio = None
            print("音频队列为空")
            return
        
        # 获取下一个音频
        audio_info = self.audio_queue.pop(0)
        self.current_audio = audio_info
        
        # 播放音频
        self.play_audio(audio_info)
        
        # 设置播放状态
        self.is_playing = True
        
        print(f"播放音频: {audio_info.get('name', '未知音频')}")
    
    def play_audio(self, audio_info):
        """播放音频"""
        sound_id = audio_info.get('sound_id')
        entity_id = audio_info.get('entity_id', 0)
        volume = audio_info.get('volume', 1.0)
        
        if not sound_id:
            print("错误: 音频信息缺少sound_id")
            self.play_next_in_queue()
            return
        
        # 计算最终音量
        final_volume = volume * self.audio_volume * self.master_volume
        
        # 创建播放音频事件
        event_data = {
            'entityId': entity_id,
            'sound': sound_id,
            'volume': final_volume
        }
        
        # 触发事件
        Event.emit('PlayCustomAudio', event_data)
        
        # 设置音频完成回调
        duration = audio_info.get('duration', 0)
        if duration > 0:
            # 使用定时器在音频结束后播放下一个
            self.level.game.AddTimer(duration, self.on_audio_complete)
    
    def on_audio_complete(self):
        """音频完成回调"""
        print(f"音频完成: {self.current_audio.get('name', '未知音频')}")
        self.play_next_in_queue()
    
    def pause_current_audio(self):
        """暂停当前音频"""
        if self.current_audio and self.is_playing:
            sound_id = self.current_audio.get('sound_id')
            if sound_id:
                # 创建停止音频事件
                event_data = {
                    'sound': sound_id
                }
                
                # 触发事件
                Event.emit('StopCustomAudio', event_data)
                
                print(f"暂停音频: {self.current_audio.get('name', '未知音频')}")
    
    def resume_current_audio(self):
        """恢复当前音频"""
        if self.current_audio and not self.is_playing:
            self.play_audio(self.current_audio)
            self.is_playing = True
            
            print(f"恢复音频: {self.current_audio.get('name', '未知音频')}")
    
    def skip_current_audio(self):
        """跳过当前音频"""
        if self.current_audio and self.is_playing:
            sound_id = self.current_audio.get('sound_id')
            if sound_id:
                # 停止当前音频
                event_data = {
                    'sound': sound_id
                }
                Event.emit('StopCustomAudio', event_data)
            
            # 播放下一个
            self.play_next_in_queue()
            
            print(f"跳过音频: {self.current_audio.get('name', '未知音频')}")
```

### 4. 游戏音频管理器

```python
from ..architect.utils.client import ClientUtilsSubsys
from ..architect.subsystem import SubsystemManager
from ..architect.event import Event

class GameAudioManager:
    def __init__(self):
        self.client_utils = SubsystemManager.getInstance().getSubsystem(ClientUtilsSubsys)
        
        # 游戏音频配置
        self.game_audio = {
            'music': {
                'main_menu': 'music.main_menu',
                'gameplay': 'music.gameplay',
                'boss_battle': 'music.boss_battle',
                'victory': 'music.victory',
                'defeat': 'music.defeat'
            },
            'sfx': {
                'ui_click': 'sfx.ui_click',
                'ui_hover': 'sfx.ui_hover',
                'player_move': 'sfx.player_move',
                'player_jump': 'sfx.player_jump