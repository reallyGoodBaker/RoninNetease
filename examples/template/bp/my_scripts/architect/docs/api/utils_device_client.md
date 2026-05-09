# 客户端设备工具 (DeviceClient) API

`architect.utils.device.client` 模块提供了客户端设备信息获取功能，包括引擎版本、IP地址、Minecraft版本、平台信息和FPS等。

## 依赖

- `...basic.clientApi` - 客户端API
- `...basic.compClient` - 客户端组件

## 类

### `deviceClient`

客户端设备工具类，提供静态方法获取设备信息。

#### 静态方法

##### `engineVer()`

获取引擎版本。

- **返回值**: 引擎版本字符串

##### `ip()`

获取客户端IP地址。

- **返回值**: IP地址字符串

##### `mcVer()`

获取Minecraft版本。

- **返回值**: Minecraft版本字符串

##### `platform()`

获取客户端平台信息。

- **返回值**: 平台标识符字符串

##### `fps()`

获取当前FPS（帧率）。

- **返回值**: FPS值（通过 `compClient.CreateGame(clientApi.GetLevelId())` 获取）

## 使用示例

### 1. 基本设备信息获取

```python
from ..architect.utils.device.client import deviceClient

class DeviceInfoManager:
    def __init__(self):
        self.device_info = {}
        self.update_device_info()
    
    def update_device_info(self):
        """更新设备信息"""
        self.device_info['engine_version'] = deviceClient.engineVer()
        self.device_info['ip_address'] = deviceClient.ip()
        self.device_info['minecraft_version'] = deviceClient.mcVer()
        self.device_info['platform'] = deviceClient.platform()
        
        # 注意：fps()方法返回的是组件对象，需要进一步处理获取FPS值
        # 这里假设有获取FPS的方法
        self.device_info['fps'] = self.get_current_fps()
        
        print("设备信息已更新")
    
    def get_current_fps(self):
        """获取当前FPS"""
        try:
            # 尝试从游戏组件获取FPS
            game_component = deviceClient.fps()
            # 这里需要根据实际API获取FPS值
            # 假设有一个GetFPS方法
            return 60  # 示例值
        except:
            return 0
    
    def get_engine_version(self):
        """获取引擎版本"""
        return self.device_info.get('engine_version', '未知')
    
    def get_ip_address(self):
        """获取IP地址"""
        return self.device_info.get('ip_address', '未知')
    
    def get_minecraft_version(self):
        """获取Minecraft版本"""
        return self.device_info.get('minecraft_version', '未知')
    
    def get_platform(self):
        """获取平台信息"""
        return self.device_info.get('platform', '未知')
    
    def get_fps(self):
        """获取FPS"""
        return self.device_info.get('fps', 0)
    
    def print_device_info(self):
        """打印设备信息"""
        print("=== 客户端设备信息 ===")
        print(f"引擎版本: {self.get_engine_version()}")
        print(f"IP地址: {self.get_ip_address()}")
        print(f"Minecraft版本: {self.get_minecraft_version()}")
        print(f"平台: {self.get_platform()}")
        print(f"当前FPS: {self.get_fps()}")
    
    def is_supported_version(self, min_version):
        """检查是否支持指定版本"""
        current_version = self.get_minecraft_version()
        # 简化版本比较
        return current_version >= min_version
    
    def get_platform_type(self):
        """获取平台类型"""
        platform_str = self.get_platform().lower()
        
        if 'windows' in platform_str:
            return 'windows'
        elif 'android' in platform_str:
            return 'android'
        elif 'ios' in platform_str:
            return 'ios'
        elif 'mac' in platform_str:
            return 'macos'
        elif 'linux' in platform_str:
            return 'linux'
        else:
            return 'unknown'
    
    def is_mobile(self):
        """检查是否为移动设备"""
        platform_type = self.get_platform_type()
        return platform_type in ['android', 'ios']
    
    def is_desktop(self):
        """检查是否为桌面设备"""
        platform_type = self.get_platform_type()
        return platform_type in ['windows', 'macos', 'linux']
```

### 2. 性能监控和适配

```python
from ..architect.utils.device.client import deviceClient
import time

class PerformanceMonitor:
    def __init__(self):
        self.fps_history = []
        self.max_history_size = 100
        self.last_update_time = time.time()
        self.update_interval = 1.0  # 1秒更新一次
        self.low_fps_threshold = 30
        self.very_low_fps_threshold = 15
        
        # 性能事件回调
        self.performance_callbacks = {
            'fps_drop': [],
            'fps_recovery': [],
            'performance_warning': []
        }
    
    def update(self):
        """更新性能监控"""
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        
        if elapsed >= self.update_interval:
            # 获取当前FPS
            current_fps = self.get_current_fps()
            
            # 添加到历史记录
            self.fps_history.append({
                'timestamp': current_time,
                'fps': current_fps
            })
            
            # 限制历史记录大小
            if len(self.fps_history) > self.max_history_size:
                self.fps_history.pop(0)
            
            # 检查性能问题
            self.check_performance_issues(current_fps)
            
            # 更新最后更新时间
            self.last_update_time = current_time
            
            return True
        
        return False
    
    def get_current_fps(self):
        """获取当前FPS"""
        try:
            # 使用deviceClient获取FPS
            # 注意：deviceClient.fps()返回的是组件对象，需要进一步处理
            # 这里使用模拟值
            return 60  # 示例值
        except:
            return 0
    
    def check_performance_issues(self, current_fps):
        """检查性能问题"""
        if current_fps < self.very_low_fps_threshold:
            # 非常低的FPS
            self.trigger_performance_event('fps_drop', {
                'fps': current_fps,
                'threshold': self.very_low_fps_threshold,
                'severity': 'critical'
            })
            print(f"性能警告: 非常低的FPS ({current_fps})")
        
        elif current_fps < self.low_fps_threshold:
            # 低的FPS
            self.trigger_performance_event('fps_drop', {
                'fps': current_fps,
                'threshold': self.low_fps_threshold,
                'severity': 'warning'
            })
            print(f"性能警告: 低的FPS ({current_fps})")
        
        else:
            # FPS正常
            if len(self.fps_history) >= 2:
                prev_fps = self.fps_history[-2]['fps']
                if prev_fps < self.low_fps_threshold and current_fps >= self.low_fps_threshold:
                    # FPS恢复
                    self.trigger_performance_event('fps_recovery', {
                        'previous_fps': prev_fps,
                        'current_fps': current_fps
                    })
                    print(f"性能恢复: FPS从 {prev_fps} 恢复到 {current_fps}")
    
    def trigger_performance_event(self, event_type, event_data):
        """触发性能事件"""
        if event_type in self.performance_callbacks:
            for callback in self.performance_callbacks[event_type]:
                callback(event_data)
    
    def add_performance_callback(self, event_type, callback):
        """添加性能回调"""
        if event_type in self.performance_callbacks:
            self.performance_callbacks[event_type].append(callback)
    
    def remove_performance_callback(self, event_type, callback):
        """移除性能回调"""
        if event_type in self.performance_callbacks and callback in self.performance_callbacks[event_type]:
            self.performance_callbacks[event_type].remove(callback)
    
    def get_average_fps(self, window_size=10):
        """获取平均FPS"""
        if not self.fps_history:
            return 0
        
        # 获取最近的数据
        recent_data = self.fps_history[-window_size:] if len(self.fps_history) >= window_size else self.fps_history
        
        # 计算平均值
        total_fps = sum(item['fps'] for item in recent_data)
        return total_fps / len(recent_data)
    
    def get_min_fps(self, window_size=10):
        """获取最小FPS"""
        if not self.fps_history:
            return 0
        
        # 获取最近的数据
        recent_data = self.fps_history[-window_size:] if len(self.fps_history) >= window_size else self.fps_history
        
        # 找到最小值
        return min(item['fps'] for item in recent_data)
    
    def get_max_fps(self, window_size=10):
        """获取最大FPS"""
        if not self.fps_history:
            return 0
        
        # 获取最近的数据
        recent_data = self.fps_history[-window_size:] if len(self.fps_history) >= window_size else self.fps_history
        
        # 找到最大值
        return max(item['fps'] for item in recent_data)
    
    def get_performance_report(self):
        """获取性能报告"""
        avg_fps = self.get_average_fps()
        min_fps = self.get_min_fps()
        max_fps = self.get_max_fps()
        
        report = {
            'average_fps': avg_fps,
            'min_fps': min_fps,
            'max_fps': max_fps,
            'fps_stability': (max_fps - min_fps) / avg_fps if avg_fps > 0 else 0,
            'performance_rating': self.calculate_performance_rating(avg_fps),
            'device_info': {
                'engine_version': deviceClient.engineVer(),
                'platform': deviceClient.platform(),
                'minecraft_version': deviceClient.mcVer()
            }
        }
        
        return report
    
    def calculate_performance_rating(self, avg_fps):
        """计算性能评级"""
        if avg_fps >= 60:
            return 'excellent'
        elif avg_fps >= 45:
            return 'good'
        elif avg_fps >= 30:
            return 'fair'
        elif avg_fps >= 15:
            return 'poor'
        else:
            return 'unplayable'
    
    def print_performance_report(self):
        """打印性能报告"""
        report = self.get_performance_report()
        
        print("=== 性能报告 ===")
        print(f"平均FPS: {report['average_fps']:.1f}")
        print(f"最小FPS: {report['min_fps']:.1f}")
        print(f"最大FPS: {report['max_fps']:.1f}")
        print(f"FPS稳定性: {report['fps_stability']:.2f}")
        print(f"性能评级: {report['performance_rating']}")
        print(f"引擎版本: {report['device_info']['engine_version']}")
        print(f"平台: {report['device_info']['platform']}")
        print(f"Minecraft版本: {report['device_info']['minecraft_version']}")
```

### 3. 设备适配和优化

```python
from ..architect.utils.device.client import deviceClient

class DeviceOptimizer:
    def __init__(self):
        self.device_info = DeviceInfoManager()
        self.performance_monitor = PerformanceMonitor()
        self.optimization_settings = {}
        self.load_default_settings()
    
    def load_default_settings(self):
        """加载默认设置"""
        self.optimization_settings = {
            'graphics': {
                'texture_quality': 'medium',
                'shadow_quality': 'medium',
                'anti_aliasing': '2x',
                'view_distance': 'normal',
                'particles': 'medium',
                'water_quality': 'medium',
                'cloud_quality': 'medium'
            },
            'audio': {
                'master_volume': 1.0,
                'music_volume': 0.8,
                'effects_volume': 1.0,
                'voice_volume': 1.0,
                '3d_audio': True
            },
            'controls': {
                'sensitivity': 0.5,
                'invert_y': False,
                'vibration': True
            }
        }
    
    def analyze_device_capabilities(self):
        """分析设备能力"""
        capabilities = {
            'platform': self.device_info.get_platform_type(),
            'is_mobile': self.device_info.is_mobile(),
            'is_desktop': self.device_info.is_desktop(),
            'engine_version': self.device_info.get_engine_version(),
            'minecraft_version': self.device_info.get_minecraft_version()
        }
        
        # 根据平台调整设置
        if capabilities['is_mobile']:
            self.optimize_for_mobile()
        elif capabilities['is_desktop']:
            self.optimize_for_desktop()
        
        print(f"设备分析完成: {capabilities['platform']}")
        return capabilities
    
    def optimize_for_mobile(self):
        """为移动设备优化"""
        self.optimization_settings['graphics'] = {
            'texture_quality': 'low',
            'shadow_quality': 'low',
            'anti_aliasing': 'off',
            'view_distance': 'short',
            'particles': 'low',
            'water_quality': 'low',
            'cloud_quality': 'low'
        }
        
        self.optimization_settings['audio'] = {
            'master_volume': 1.0,
            'music_volume': 0.7,
            'effects_volume': 0.9,
            'voice_volume': 1.0,
            '3d_audio': False  # 移动设备可能不支持3D音频
        }
        
        self.optimization_settings['controls'] = {
            'sensitivity': 0.3,
            'invert_y': False,
            'vibration': True
        }
        
        print("已应用移动设备优化设置")
    
    def optimize_for_desktop(self):
        """为桌面设备优化"""
        # 获取FPS信息以决定优化级别
        avg_fps = self.performance_monitor.get_average_fps()
        
        if avg_fps >= 60:
            self.optimization_settings['graphics'] = {
                'texture_quality': 'high',
                'shadow_quality': 'high',
                'anti_aliasing': '4x',
                'view_distance': 'far',
                'particles': 'high',
                'water_quality': 'high',
                'cloud_quality': 'high'
            }
            print("已应用高性能桌面优化设置")
        
        elif avg_fps >= 30:
            self.optimization_settings['graphics'] = {
                'texture_quality': 'medium',
                'shadow_quality': 'medium',
                'anti_aliasing': '2x',
                'view_distance': 'normal',
                'particles': 'medium',
                'water_quality': 'medium',
                'cloud_quality': 'medium'
            }
            print("已应用中性能桌面优化设置")
        
        else:
            self.optimization_settings['graphics'] = {
                'texture_quality': 'low',
                'shadow_quality': 'low',
                'anti_aliasing': 'off',
                'view_distance': 'short',
                'particles': 'low',
                'water_quality': 'low',
                'cloud_quality': 'low'
            }
            print("已应用低性能桌面优化设置")
    
    def dynamic_optimization(self):
        """动态优化"""
        # 监控性能
        self.performance_monitor.update()
        
        # 获取性能报告
        report = self.performance_monitor.get_performance_report()
        
        # 根据性能调整设置
        if report['performance_rating'] == 'unplayable':
            self.apply_lowest_settings()
            print("应用最低设置以改善性能")
        
        elif report['performance_rating'] == 'poor':
            self.reduce_graphics_quality()
            print("降低图形质量以改善性能")
        
        elif report['performance_rating'] == 'excellent':
            # 如果性能优秀，可以尝试提高质量
            self.improve_graphics_quality()
            print("提高图形质量以利用额外性能")
    
    def apply_lowest_settings(self):
        """应用最低设置"""
        self.optimization_settings['graphics'] = {
            'texture_quality': 'very_low',
            'shadow_quality': 'off',
            'anti_aliasing': 'off',
            'view_distance': 'very_short',
            'particles': 'off',
            'water_quality': 'off',
            'cloud_quality': 'off'
        }
    
    def reduce_graphics_quality(self):
        """降低图形质量"""
        graphics = self.optimization_settings['graphics']
        
        # 逐步降低质量
        quality_levels = ['ultra', 'high', 'medium', 'low', 'very_low', 'off']
        
        for setting in ['texture_quality', 'shadow_quality', 'anti_aliasing']:
            if setting in graphics:
                current = graphics[setting]
                if current in quality_levels:
                    current_index = quality_levels.index(current)
                    if current_index < len(quality_levels) - 1:
                        graphics[setting] = quality_levels[current_index + 1]
    
    def improve_graphics_quality(self):
        """提高图形质量"""
        graphics = self.optimization_settings['graphics']
        
        # 逐步提高质量
        quality_levels = ['off', 'very_low', 'low', 'medium', 'high', 'ultra']
        
        for setting in ['texture_quality', 'shadow_quality', 'anti_aliasing']:
            if setting in graphics:
                current = graphics[setting]
                if current in quality_levels:
                    current_index = quality_levels.index(current)
