# 服务端设备工具 (DeviceServer) API

`architect.utils.device.server` 模块提供了服务端设备信息获取功能，包括Minecraft版本、平台信息和运行环境检测等。

## 依赖

- `...basic.serverApi` - 服务端API

## 类

### `deviceServer`

服务端设备工具类，提供静态方法获取设备信息。

#### 静态方法

##### `mcVer()`

获取服务端Minecraft版本。

- **返回值**: Minecraft版本字符串

##### `platform()`

获取服务端平台信息。

- **返回值**: 平台标识符字符串

##### `inApollo()`

检查是否在Apollo环境中运行。

- **返回值**: 布尔值，True表示在Apollo环境中

##### `inServer()`

检查是否在服务器环境中运行。

- **返回值**: 布尔值，True表示在服务器环境中

## 使用示例

### 1. 基本服务端设备信息获取

```python
from ..architect.utils.device.server import deviceServer

class ServerDeviceInfo:
    def __init__(self):
        self.server_info = {}
        self.update_server_info()
    
    def update_server_info(self):
        """更新服务端信息"""
        self.server_info['minecraft_version'] = deviceServer.mcVer()
        self.server_info['platform'] = deviceServer.platform()
        self.server_info['in_apollo'] = deviceServer.inApollo()
        self.server_info['in_server'] = deviceServer.inServer()
        
        print("服务端信息已更新")
    
    def get_minecraft_version(self):
        """获取Minecraft版本"""
        return self.server_info.get('minecraft_version', '未知')
    
    def get_platform(self):
        """获取平台信息"""
        return self.server_info.get('platform', '未知')
    
    def is_in_apollo(self):
        """检查是否在Apollo环境中"""
        return self.server_info.get('in_apollo', False)
    
    def is_in_server(self):
        """检查是否在服务器环境中"""
        return self.server_info.get('in_server', False)
    
    def print_server_info(self):
        """打印服务端信息"""
        print("=== 服务端设备信息 ===")
        print(f"Minecraft版本: {self.get_minecraft_version()}")
        print(f"平台: {self.get_platform()}")
        print(f"在Apollo环境中: {'是' if self.is_in_apollo() else '否'}")
        print(f"在服务器环境中: {'是' if self.is_in_server() else '否'}")
    
    def get_platform_type(self):
        """获取平台类型"""
        platform_str = self.get_platform().lower()
        
        if 'windows' in platform_str:
            return 'windows'
        elif 'linux' in platform_str:
            return 'linux'
        elif 'mac' in platform_str:
            return 'macos'
        elif 'android' in platform_str:
            return 'android'
        else:
            return 'unknown'
    
    def is_dedicated_server(self):
        """检查是否为专用服务器"""
        # 如果在服务器环境中且不在Apollo环境中，可能是专用服务器
        return self.is_in_server() and not self.is_in_apollo()
    
    def is_apollo_server(self):
        """检查是否为Apollo服务器"""
        return self.is_in_apollo()
    
    def get_server_type(self):
        """获取服务器类型"""
        if self.is_apollo_server():
            return 'apollo'
        elif self.is_dedicated_server():
            return 'dedicated'
        else:
            return 'unknown'
```

### 2. 服务器环境适配

```python
from ..architect.utils.device.server import deviceServer

class ServerEnvironmentAdapter:
    def __init__(self):
        self.server_info = ServerDeviceInfo()
        self.environment_settings = {}
        self.load_environment_settings()
    
    def load_environment_settings(self):
        """加载环境设置"""
        # 根据服务器类型加载不同的设置
        server_type = self.server_info.get_server_type()
        
        if server_type == 'apollo':
            self.environment_settings = {
                'max_players': 10,
                'view_distance': 6,
                'simulation_distance': 4,
                'tick_rate': 20,
                'entity_limit': 100,
                'chunk_loading': 'lazy',
                'performance_mode': 'balanced'
            }
            print("已加载Apollo服务器设置")
        
        elif server_type == 'dedicated':
            self.environment_settings = {
                'max_players': 50,
                'view_distance': 10,
                'simulation_distance': 8,
                'tick_rate': 20,
                'entity_limit': 500,
                'chunk_loading': 'eager',
                'performance_mode': 'performance'
            }
            print("已加载专用服务器设置")
        
        else:
            self.environment_settings = {
                'max_players': 20,
                'view_distance': 8,
                'simulation_distance': 6,
                'tick_rate': 20,
                'entity_limit': 200,
                'chunk_loading': 'normal',
                'performance_mode': 'balanced'
            }
            print("已加载默认服务器设置")
    
    def optimize_for_environment(self):
        """根据环境优化"""
        server_type = self.server_info.get_server_type()
        platform_type = self.server_info.get_platform_type()
        
        print(f"服务器类型: {server_type}, 平台: {platform_type}")
        
        if server_type == 'apollo':
            self.optimize_for_apollo()
        elif server_type == 'dedicated':
            self.optimize_for_dedicated_server()
        
        if platform_type == 'linux':
            self.optimize_for_linux()
        elif platform_type == 'windows':
            self.optimize_for_windows()
    
    def optimize_for_apollo(self):
        """为Apollo环境优化"""
        # Apollo环境通常资源有限，需要更保守的设置
        self.environment_settings['max_players'] = min(self.environment_settings['max_players'], 8)
        self.environment_settings['view_distance'] = min(self.environment_settings['view_distance'], 4)
        self.environment_settings['simulation_distance'] = min(self.environment_settings['simulation_distance'], 3)
        self.environment_settings['entity_limit'] = min(self.environment_settings['entity_limit'], 50)
        self.environment_settings['performance_mode'] = 'conservative'
        
        print("已应用Apollo环境优化")
    
    def optimize_for_dedicated_server(self):
        """为专用服务器优化"""
        # 专用服务器通常有更多资源，可以使用更激进的设置
        self.environment_settings['max_players'] = 100
        self.environment_settings['view_distance'] = 12
        self.environment_settings['simulation_distance'] = 10
        self.environment_settings['entity_limit'] = 1000
        self.environment_settings['performance_mode'] = 'performance'
        
        print("已应用专用服务器优化")
    
    def optimize_for_linux(self):
        """为Linux平台优化"""
        # Linux服务器通常更稳定，可以启用更多功能
        self.environment_settings['chunk_loading'] = 'eager'
        self.environment_settings['tick_rate'] = 20  # 标准tick率
        
        print("已应用Linux平台优化")
    
    def optimize_for_windows(self):
        """为Windows平台优化"""
        # Windows服务器可能需要更保守的设置
        self.environment_settings['chunk_loading'] = 'normal'
        self.environment_settings['tick_rate'] = 20
        
        print("已应用Windows平台优化")
    
    def get_environment_settings(self):
        """获取环境设置"""
        return self.environment_settings
    
    def apply_environment_settings(self):
        """应用环境设置"""
        print("=== 应用环境设置 ===")
        for key, value in self.environment_settings.items():
            print(f"{key}: {value}")
        
        # 这里可以添加实际应用设置的代码
        # 例如：设置服务器属性、调整配置等
        
        return True
    
    def validate_environment(self):
        """验证环境"""
        issues = []
        
        # 检查Minecraft版本
        mc_version = self.server_info.get_minecraft_version()
        if not mc_version:
            issues.append("无法获取Minecraft版本")
        
        # 检查服务器环境
        if not self.server_info.is_in_server():
            issues.append("不在服务器环境中运行")
        
        # 检查平台兼容性
        platform_type = self.server_info.get_platform_type()
        if platform_type == 'unknown':
            issues.append("未知平台类型")
        
        if issues:
            print("环境验证发现问题:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("环境验证通过")
            return True
```

### 3. 服务器性能监控

```python
from ..architect.utils.device.server import deviceServer
import time
import threading

class ServerPerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'tps': 20,  # 每秒刻数
            'player_count': 0,
            'entity_count': 0,
            'chunk_count': 0,
            'memory_usage': 0,
            'cpu_usage': 0,
            'network_bandwidth': 0
        }
        
        self.history = {
            'tps': [],
            'player_count': [],
            'memory_usage': []
        }
        
        self.max_history_length = 100
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 性能阈值
        self.thresholds = {
            'tps_low': 15,
            'tps_very_low': 10,
            'memory_warning': 80,  # 百分比
            'memory_critical': 90,
            'player_warning': 80,  # 相对于最大玩家数
            'player_critical': 95
        }
        
        # 性能事件回调
        self.performance_events = {
            'tps_drop': [],
            'memory_warning': [],
            'high_player_count': [],
            'performance_improved': []
        }
    
    def start_monitoring(self, interval=5.0):
        """开始性能监控"""
        if self.is_monitoring:
            print("性能监控已在运行")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"服务器性能监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        print("服务器性能监控已停止")
    
    def monitoring_loop(self, interval):
        """监控循环"""
        while self.is_monitoring:
            # 更新性能指标
            self.update_performance_metrics()
            
            # 检查性能问题
            self.check_performance_issues()
            
            # 等待
            time.sleep(interval)
    
    def update_performance_metrics(self):
        """更新性能指标"""
        # 模拟获取性能数据
        import random
        
        # TPS（每秒刻数）
        self.metrics['tps'] = random.uniform(18, 20)
        
        # 玩家数量
        self.metrics['player_count'] = random.randint(0, 50)
        
        # 实体数量
        self.metrics['entity_count'] = random.randint(100, 1000)
        
        # 区块数量
        self.metrics['chunk_count'] = random.randint(500, 5000)
        
        # 内存使用率
        self.metrics['memory_usage'] = random.uniform(30, 80)
        
        # CPU使用率
        self.metrics['cpu_usage'] = random.uniform(10, 60)
        
        # 网络带宽
        self.metrics['network_bandwidth'] = random.uniform(1, 10)  # Mbps
        
        # 保存到历史记录
        self.add_to_history('tps', self.metrics['tps'])
        self.add_to_history('player_count', self.metrics['player_count'])
        self.add_to_history('memory_usage', self.metrics['memory_usage'])
    
    def add_to_history(self, metric_name, value):
        """添加到历史记录"""
        if metric_name in self.history:
            self.history[metric_name].append(value)
            
            # 限制历史记录长度
            if len(self.history[metric_name]) > self.max_history_length:
                self.history[metric_name].pop(0)
    
    def check_performance_issues(self):
        """检查性能问题"""
        # 检查TPS下降
        if self.metrics['tps'] < self.thresholds['tps_very_low']:
            self.trigger_performance_event('tps_drop', {
                'tps': self.metrics['tps'],
                'threshold': self.thresholds['tps_very_low'],
                'severity': 'critical'
            })
            print(f"性能警告: 非常低的TPS ({self.metrics['tps']:.1f})")
        
        elif self.metrics['tps'] < self.thresholds['tps_low']:
            self.trigger_performance_event('tps_drop', {
                'tps': self.metrics['tps'],
                'threshold': self.thresholds['tps_low'],
                'severity': 'warning'
            })
            print(f"性能警告: 低的TPS ({self.metrics['tps']:.1f})")
        
        # 检查内存使用率
        if self.metrics['memory_usage'] > self.thresholds['memory_critical']:
            self.trigger_performance_event('memory_warning', {
                'memory_usage': self.metrics['memory_usage'],
                'threshold': self.thresholds['memory_critical'],
                'severity': 'critical'
            })
            print(f"性能警告: 严重的内存使用率 ({self.metrics['memory_usage']:.1f}%)")
        
        elif self.metrics['memory_usage'] > self.thresholds['memory_warning']:
            self.trigger_performance_event('memory_warning', {
                'memory_usage': self.metrics['memory_usage'],
                'threshold': self.thresholds['memory_warning'],
                'severity': 'warning'
            })
            print(f"性能警告: 高的内存使用率 ({self.metrics['memory_usage']:.1f}%)")
        
        # 检查玩家数量
        max_players = 50  # 假设最大玩家数
        player_percentage = (self.metrics['player_count'] / max_players) * 100
        
        if player_percentage > self.thresholds['player_critical']:
            self.trigger_performance_event('high_player_count', {
                'player_count': self.metrics['player_count'],
                'max_players': max_players,
                'percentage': player_percentage,
                'severity': 'critical'
            })
            print(f"玩家警告: 接近满员 ({self.metrics['player_count']}/{max_players})")
        
        elif player_percentage > self.thresholds['player_warning']:
            self.trigger_performance_event('high_player_count', {
                'player_count': self.metrics['player_count'],
                'max_players': max_players,
                'percentage': player_percentage,
                'severity': 'warning'
            })
            print(f"玩家警告: 高玩家数量 ({self.metrics['player_count']}/{max_players})")
    
    def trigger_performance_event(self, event_type, event_data):
        """触发性能事件"""
        if event_type in self.performance_events:
            for callback in self.performance_events[event_type]:
                callback(event_data)
    
    def add_performance_callback(self, event_type, callback):
        """添加性能回调"""
        if event_type in self.performance_events:
            self.performance_events[event_type].append(callback)
    
    def remove_performance_callback(self, event_type, callback):
        """移除性能回调"""
        if event_type in self.performance_events and callback in self.performance_events[event_type]:
            self.performance_events[event_type].remove(callback)
    
    def get_performance_report(self):
        """获取性能报告"""
        report = {
            'tps': {
                'current': self.metrics['tps'],
                'average': self.calculate_average('tps'),
                'min': self.calculate_min('tps'),
                'max': self.calculate_max('tps')
            },
            'players': {
                'current': self.metrics['player_count'],
                'average': self.calculate_average('player_count'),
                'trend': self.calculate_trend('player_count')
            },
            'memory': {
                'current': self.metrics['memory_usage'],
                'average': self.calculate_average('memory_usage'),
                'status': self.get_memory_status()
            },
            'entities': self.metrics['entity_count'],
            'chunks': self.metrics['chunk_count'],
            'cpu': self.metrics['cpu_usage'],
            'network': self.metrics['network_bandwidth'],
            'server_info': {
                'minecraft_version': deviceServer.mcVer(),
                'platform': deviceServer.platform(),
                'in_apollo': deviceServer.inApollo(),
                'in_server': deviceServer.inServer()
            }
        }
        
        return report
    
    def calculate_average(self, metric_name):
        """计算平均值"""
        if metric_name in self.history and self.history[metric_name]:
            return sum(self.history[metric_name]) / len(self.history[metric_name])
        return 0
    
    def calculate_min(self, metric_name):
        """计算最小值"""
        if metric_name in self.history and self.history[metric_name]:
            return min(self.history[metric_name])
        return 0
    
    def calculate_max(self, metric_name):
        """计算最大值"""
        if metric_name in self.history and self.history[metric_name]:
            return max(self.history[metric_name])
        return 0
    
    def calculate_trend(self, metric_name):
        """计算趋势