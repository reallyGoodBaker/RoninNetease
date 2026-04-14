# 设备工具 (Device) API

`architect.utils.device` 模块提供了设备相关的工具功能，用于检测和管理客户端设备信息。

## 模块结构

`architect.utils.device` 模块包含以下子模块：

- `architect.utils.device.client` - 客户端设备工具
- `architect.utils.device.server` - 服务端设备工具

## 使用示例

### 1. 基本设备检测

```python
import platform
import sys
import os

class DeviceDetector:
    def __init__(self):
        self.device_info = {}
        self.detect_device()
    
    def detect_device(self):
        """检测设备信息"""
        # 操作系统信息
        self.device_info['os'] = {
            'name': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'architecture': platform.architecture()[0]
        }
        
        # Python信息
        self.device_info['python'] = {
            'version': platform.python_version(),
            'implementation': platform.python_implementation(),
            'compiler': platform.python_compiler()
        }
        
        # 硬件信息
        self.device_info['hardware'] = {
            'processor': platform.processor(),
            'machine': platform.machine(),
            'node': platform.node()
        }
        
        # 内存信息（简化）
        try:
            import psutil
            memory = psutil.virtual_memory()
            self.device_info['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent
            }
        except ImportError:
            self.device_info['memory'] = {
                'total': 0,
                'available': 0,
                'percent': 0
            }
        
        print("设备信息检测完成")
    
    def get_os_info(self):
        """获取操作系统信息"""
        return self.device_info['os']
    
    def get_python_info(self):
        """获取Python信息"""
        return self.device_info['python']
    
    def get_hardware_info(self):
        """获取硬件信息"""
        return self.device_info['hardware']
    
    def get_memory_info(self):
        """获取内存信息"""
        return self.device_info['memory']
    
    def get_all_info(self):
        """获取所有设备信息"""
        return self.device_info
    
    def is_windows(self):
        """检查是否为Windows系统"""
        return self.device_info['os']['name'] == 'Windows'
    
    def is_linux(self):
        """检查是否为Linux系统"""
        return self.device_info['os']['name'] == 'Linux'
    
    def is_mac(self):
        """检查是否为macOS系统"""
        return self.device_info['os']['name'] == 'Darwin'
    
    def is_64bit(self):
        """检查是否为64位系统"""
        return self.device_info['os']['architecture'] == '64bit'
    
    def get_os_version_string(self):
        """获取操作系统版本字符串"""
        os_info = self.device_info['os']
        return f"{os_info['name']} {os_info['release']} ({os_info['version']})"
    
    def get_python_version_string(self):
        """获取Python版本字符串"""
        python_info = self.device_info['python']
        return f"{python_info['implementation']} {python_info['version']}"
    
    def get_memory_string(self):
        """获取内存信息字符串"""
        memory_info = self.device_info['memory']
        if memory_info['total'] > 0:
            total_gb = memory_info['total'] / (1024**3)
            available_gb = memory_info['available'] / (1024**3)
            return f"{available_gb:.1f}GB / {total_gb:.1f}GB ({memory_info['percent']}%)"
        return "未知"
    
    def print_device_info(self):
        """打印设备信息"""
        print("=== 设备信息 ===")
        print(f"操作系统: {self.get_os_version_string()}")
        print(f"Python: {self.get_python_version_string()}")
        print(f"处理器: {self.device_info['hardware']['processor']}")
        print(f"内存: {self.get_memory_string()}")
        print(f"机器类型: {self.device_info['hardware']['machine']}")
        print(f"主机名: {self.device_info['hardware']['node']}")
```

### 2. 游戏设备适配

```python
class GameDeviceAdapter:
    def __init__(self):
        self.detector = DeviceDetector()
        self.device_capabilities = {}
        self.detect_capabilities()
    
    def detect_capabilities(self):
        """检测设备能力"""
        # 图形能力
        self.device_capabilities['graphics'] = {
            'max_texture_size': self.detect_max_texture_size(),
            'shader_support': self.detect_shader_support(),
            'anti_aliasing': self.detect_anti_aliasing_support(),
            'shadow_quality': self.detect_shadow_quality()
        }
        
        # 输入设备
        self.device_capabilities['input'] = {
            'keyboard': True,
            'mouse': True,
            'gamepad': self.detect_gamepad_support(),
            'touch': self.detect_touch_support()
        }
        
        # 音频能力
        self.device_capabilities['audio'] = {
            'channels': self.detect_audio_channels(),
            'sample_rate': self.detect_audio_sample_rate(),
            '3d_audio': self.detect_3d_audio_support()
        }
        
        # 网络能力
        self.device_capabilities['network'] = {
            'bandwidth': self.estimate_bandwidth(),
            'latency': self.estimate_latency(),
            'stable': self.check_network_stability()
        }
        
        print("设备能力检测完成")
    
    def detect_max_texture_size(self):
        """检测最大纹理尺寸"""
        # 根据内存估算最大纹理尺寸
        memory_info = self.detector.get_memory_info()
        total_memory_gb = memory_info['total'] / (1024**3)
        
        if total_memory_gb >= 16:
            return 8192  # 8K纹理
        elif total_memory_gb >= 8:
            return 4096  # 4K纹理
        elif total_memory_gb >= 4:
            return 2048  # 2K纹理
        else:
            return 1024  # 1K纹理
    
    def detect_shader_support(self):
        """检测着色器支持"""
        # 根据操作系统和硬件估算
        if self.detector.is_windows():
            # Windows通常有较好的着色器支持
            return "high"
        elif self.detector.is_mac():
            # macOS支持Metal着色器
            return "medium"
        else:
            # Linux支持情况各异
            return "basic"
    
    def detect_anti_aliasing_support(self):
        """检测抗锯齿支持"""
        # 根据内存和图形能力估算
        memory_info = self.detector.get_memory_info()
        if memory_info['total'] >= 8 * (1024**3):  # 8GB以上
            return "8x"
        elif memory_info['total'] >= 4 * (1024**3):  # 4GB以上
            return "4x"
        else:
            return "2x"
    
    def detect_shadow_quality(self):
        """检测阴影质量"""
        memory_info = self.detector.get_memory_info()
        if memory_info['total'] >= 8 * (1024**3):
            return "ultra"
        elif memory_info['total'] >= 4 * (1024**3):
            return "high"
        elif memory_info['total'] >= 2 * (1024**3):
            return "medium"
        else:
            return "low"
    
    def detect_gamepad_support(self):
        """检测游戏手柄支持"""
        # 检查是否有游戏手柄驱动
        try:
            import pygame
            pygame.init()
            joystick_count = pygame.joystick.get_count()
            pygame.quit()
            return joystick_count > 0
        except:
            return False
    
    def detect_touch_support(self):
        """检测触摸屏支持"""
        # 检查是否为移动设备或触摸屏设备
        os_name = self.detector.get_os_info()['name']
        return os_name in ['Android', 'iOS'] or self.detector.is_mac()
    
    def detect_audio_channels(self):
        """检测音频通道数"""
        # 根据操作系统估算
        if self.detector.is_windows():
            return 7.1  # Windows通常支持7.1声道
        elif self.detector.is_mac():
            return 5.1  # macOS通常支持5.1声道
        else:
            return 2.0  # Linux通常支持立体声
    
    def detect_audio_sample_rate(self):
        """检测音频采样率"""
        return 44100  # 标准CD音质
    
    def detect_3d_audio_support(self):
        """检测3D音频支持"""
        return True  # 大多数现代设备都支持
    
    def estimate_bandwidth(self):
        """估算网络带宽"""
        # 简化估算
        return 10.0  # 10 Mbps
    
    def estimate_latency(self):
        """估算网络延迟"""
        # 简化估算
        return 50  # 50ms
    
    def check_network_stability(self):
        """检查网络稳定性"""
        return True  # 假设网络稳定
    
    def get_recommended_graphics_settings(self):
        """获取推荐的图形设置"""
        memory_info = self.detector.get_memory_info()
        total_memory_gb = memory_info['total'] / (1024**3)
        
        if total_memory_gb >= 16:
            return {
                'texture_quality': 'ultra',
                'shadow_quality': 'ultra',
                'anti_aliasing': '8x',
                'view_distance': 'far',
                'particles': 'high',
                'water_quality': 'high',
                'cloud_quality': 'high'
            }
        elif total_memory_gb >= 8:
            return {
                'texture_quality': 'high',
                'shadow_quality': 'high',
                'anti_aliasing': '4x',
                'view_distance': 'normal',
                'particles': 'medium',
                'water_quality': 'medium',
                'cloud_quality': 'medium'
            }
        elif total_memory_gb >= 4:
            return {
                'texture_quality': 'medium',
                'shadow_quality': 'medium',
                'anti_aliasing': '2x',
                'view_distance': 'short',
                'particles': 'low',
                'water_quality': 'low',
                'cloud_quality': 'low'
            }
        else:
            return {
                'texture_quality': 'low',
                'shadow_quality': 'low',
                'anti_aliasing': 'off',
                'view_distance': 'very_short',
                'particles': 'off',
                'water_quality': 'off',
                'cloud_quality': 'off'
            }
    
    def get_recommended_audio_settings(self):
        """获取推荐的音频设置"""
        return {
            'master_volume': 1.0,
            'music_volume': 0.8,
            'effects_volume': 1.0,
            'voice_volume': 1.0,
            '3d_audio': True,
            'environmental_effects': True
        }
    
    def get_recommended_control_settings(self):
        """获取推荐的控制设置"""
        has_gamepad = self.device_capabilities['input']['gamepad']
        has_touch = self.device_capabilities['input']['touch']
        
        if has_gamepad:
            return {
                'primary_input': 'gamepad',
                'keyboard_mouse': True,
                'touch_controls': has_touch,
                'vibration': True,
                'sensitivity': 0.5
            }
        elif has_touch:
            return {
                'primary_input': 'touch',
                'keyboard_mouse': False,
                'touch_controls': True,
                'vibration': False,
                'sensitivity': 0.3
            }
        else:
            return {
                'primary_input': 'keyboard_mouse',
                'keyboard_mouse': True,
                'touch_controls': False,
                'vibration': False,
                'sensitivity': 0.7
            }
    
    def apply_optimized_settings(self):
        """应用优化设置"""
        graphics_settings = self.get_recommended_graphics_settings()
        audio_settings = self.get_recommended_audio_settings()
        control_settings = self.get_recommended_control_settings()
        
        print("=== 优化设置 ===")
        print("图形设置:")
        for key, value in graphics_settings.items():
            print(f"  {key}: {value}")
        
        print("\n音频设置:")
        for key, value in audio_settings.items():
            print(f"  {key}: {value}")
        
        print("\n控制设置:")
        for key, value in control_settings.items():
            print(f"  {key}: {value}")
        
        return {
            'graphics': graphics_settings,
            'audio': audio_settings,
            'controls': control_settings
        }
```

### 3. 性能监控

```python
import time
import threading

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'fps': 0,
            'frame_time': 0,
            'memory_usage': 0,
            'cpu_usage': 0,
            'gpu_usage': 0,
            'network_latency': 0
        }
        
        self.history = {
            'fps': [],
            'frame_time': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        
        self.max_history_length = 100
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 性能阈值
        self.thresholds = {
            'fps_low': 30,
            'fps_very_low': 15,
            'memory_warning': 80,  # 百分比
            'memory_critical': 90,
            'cpu_warning': 70,
            'cpu_critical': 90
        }
        
        # 性能事件回调
        self.performance_events = {
            'fps_drop': [],
            'memory_warning': [],
            'cpu_warning': [],
            'performance_improved': []
        }
    
    def start_monitoring(self, interval=1.0):
        """开始性能监控"""
        if self.is_monitoring:
            print("性能监控已在运行")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"性能监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        print("性能监控已停止")
    
    def monitoring_loop(self, interval):
        """监控循环"""
        frame_count = 0
        last_time = time.time()
        
        while self.is_monitoring:
            current_time = time.time()
            elapsed = current_time - last_time
            
            if elapsed >= interval:
                # 计算FPS
                if frame_count > 0:
                    self.metrics['fps'] = frame_count / elapsed
                    self.metrics['frame_time'] = 1000.0 / self.metrics['fps'] if self.metrics['fps'] > 0 else 0
                
                # 更新其他指标
                self.update_performance_metrics()
                
                # 检查性能问题
                self.check_performance_issues()
                
                # 重置计数器
                frame_count = 0
                last_time = current_time
            
            # 模拟帧计数
            frame_count += 1
            
            # 等待
            time.sleep(0.016)  # 约60Hz
    
    def update_performance_metrics(self):
        """更新性能指标"""
        # 模拟获取性能数据
        import random
        
        # 内存使用率
        try:
            import psutil
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'] = memory.percent
        except:
            self.metrics['memory_usage'] = random.uniform(30, 70)
        
        # CPU使用率
        try:
            import psutil
            self.metrics['cpu_usage'] = psutil.cpu_percent(interval=0.1)
        except:
            self.metrics['cpu_usage'] = random.uniform(10, 50)
        
        # GPU使用率（简化）
        self.metrics['gpu_usage'] = random.uniform(10, 60)
        
        # 网络延迟
        self.metrics['network_latency'] = random.uniform(20, 100)
        
        # 保存到历史记录
        self.add_to_history('fps', self.metrics['fps'])
        self.add_to_history('frame_time', self.metrics['frame_time'])
        self.add_to_history('memory_usage', self.metrics['memory_usage'])
        self.add_to_history('cpu_usage', self.metrics['cpu_usage'])
    
    def add_to_history(self, metric_name, value):
        """添加到历史记录"""
        if metric_name in self.history:
            self.history[metric_name].append(value)
            
            # 限制历史记录长度
            if len(self.history[metric_name]) > self.max_history_length:
                self.history[metric_name].pop(0)
    
    def check_performance_issues(self):
        """检查性能问题"""
        # 检查FPS下降
        if self.metrics['fps'] < self.thresholds['fps_very_low']:
            self.