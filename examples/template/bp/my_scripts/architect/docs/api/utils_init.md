# 工具模块 (Utils) API

`architect.utils` 模块提供了各种实用工具和辅助功能，用于简化开发过程和提高代码复用性。

## 模块结构

`architect.utils` 模块包含以下子模块：

- `architect.utils.client` - 客户端工具
- `architect.utils.loader` - 资源加载器
- `architect.utils.server` - 服务端工具
- `architect.utils.device` - 设备工具
- `architect.utils.enhance` - 增强工具
- `architect.utils.molang` - MoLang表达式工具
- `architect.utils.persona` - 角色工具

## 使用示例

### 1. 基本导入

```python
# 导入整个utils模块
from ..architect.utils import *

# 或者导入特定子模块
from ..architect.utils.client import ClientUtils
from ..architect.utils.loader import ResourceLoader
from ..architect.utils.server import ServerUtils
from ..architect.utils.device import DeviceInfo
from ..architect.utils.enhance import EnhancedList
from ..architect.utils.molang import MoLangParser
from ..architect.utils.persona import PersonaManager
```

### 2. 动画淡入淡出工具

```python
from ..architect.utils.animFader import AnimFader

class FadeManager:
    def __init__(self):
        self.faders = {}
    
    def create_fade(self, name, duration=1.0, start_value=0.0, end_value=1.0):
        """创建淡入淡出动画"""
        fader = AnimFader(duration, start_value, end_value)
        self.faders[name] = fader
        return fader
    
    def update_fades(self, delta_time):
        """更新所有淡入淡出动画"""
        for name, fader in self.faders.items():
            fader.update(delta_time)
            
            # 检查是否完成
            if fader.is_complete():
                print(f"淡入淡出动画 '{name}' 完成")
                # 可以在这里触发完成事件
    
    def fade_in_ui(self, ui_element, duration=0.5):
        """淡入UI元素"""
        fader = self.create_fade(f"fade_in_{ui_element.id}", duration, 0.0, 1.0)
        
        def update_alpha(value):
            ui_element.alpha = value
        
        fader.on_update = update_alpha
        fader.start()
    
    def fade_out_ui(self, ui_element, duration=0.5):
        """淡出UI元素"""
        fader = self.create_fade(f"fade_out_{ui_element.id}", duration, 1.0, 0.0)
        
        def update_alpha(value):
            ui_element.alpha = value
        
        fader.on_update = update_alpha
        fader.start()
        
        # 动画完成后隐藏元素
        def on_complete():
            ui_element.visible = False
        
        fader.on_complete = on_complete
```

### 3. 客户端工具

```python
from ..architect.utils.client import ClientUtils

class GameClient:
    def __init__(self):
        self.utils = ClientUtils()
        self.setup_client()
    
    def setup_client(self):
        """设置客户端"""
        # 获取客户端信息
        client_info = self.utils.get_client_info()
        print(f"客户端版本: {client_info['version']}")
        print(f"客户端平台: {client_info['platform']}")
        print(f"客户端语言: {client_info['language']}")
        
        # 检查网络连接
        if self.utils.is_online():
            print("客户端在线")
        else:
            print("客户端离线")
        
        # 获取设备性能信息
        performance = self.utils.get_performance_info()
        print(f"帧率: {performance['fps']} FPS")
        print(f"内存使用: {performance['memory_usage']} MB")
        print(f"CPU使用率: {performance['cpu_usage']}%")
    
    def optimize_graphics(self):
        """优化图形设置"""
        # 根据设备性能调整图形质量
        performance = self.utils.get_performance_info()
        
        if performance['fps'] < 30:
            # 帧率低，降低图形质量
            self.utils.set_graphics_quality("low")
            print("图形质量已设置为: 低")
        elif performance['fps'] < 60:
            # 帧率中等，使用中等图形质量
            self.utils.set_graphics_quality("medium")
            print("图形质量已设置为: 中")
        else:
            # 帧率高，使用高图形质量
            self.utils.set_graphics_quality("high")
            print("图形质量已设置为: 高")
    
    def handle_screen_resize(self, width, height):
        """处理屏幕尺寸变化"""
        # 更新UI布局
        self.utils.update_ui_layout(width, height)
        
        # 调整相机视野
        self.utils.adjust_camera_fov(width, height)
        
        print(f"屏幕尺寸已更新: {width}x{height}")
    
    def save_client_data(self):
        """保存客户端数据"""
        game_data = {
            "player_name": "玩家1",
            "level": 5,
            "experience": 1200,
            "settings": {
                "volume": 80,
                "graphics": "medium",
                "controls": "default"
            }
        }
        
        # 保存到本地存储
        success = self.utils.save_local_data("game_save", game_data)
        
        if success:
            print("游戏数据已保存")
        else:
            print("保存游戏数据失败")
    
    def load_client_data(self):
        """加载客户端数据"""
        # 从本地存储加载
        game_data = self.utils.load_local_data("game_save")
        
        if game_data:
            print(f"加载玩家: {game_data['player_name']}")
            print(f"玩家等级: {game_data['level']}")
            print(f"玩家经验: {game_data['experience']}")
            return game_data
        else:
            print("加载游戏数据失败，使用默认值")
            return self.get_default_game_data()
```

### 4. 资源加载器

```python
from ..architect.utils.loader import ResourceLoader

class ResourceManager:
    def __init__(self):
        self.loader = ResourceLoader()
        self.resources = {}
        self.loading_queue = []
        self.is_loading = False
    
    def preload_resources(self, resource_list):
        """预加载资源"""
        print(f"开始预加载 {len(resource_list)} 个资源")
        
        for resource in resource_list:
            self.load_resource_async(resource['type'], resource['path'], resource['id'])
    
    def load_resource_async(self, resource_type, path, resource_id):
        """异步加载资源"""
        # 添加到加载队列
        self.loading_queue.append({
            'type': resource_type,
            'path': path,
            'id': resource_id
        })
        
        # 如果没有正在加载，开始加载
        if not self.is_loading:
            self.process_loading_queue()
    
    def process_loading_queue(self):
        """处理加载队列"""
        if not self.loading_queue:
            self.is_loading = False
            print("所有资源加载完成")
            return
        
        self.is_loading = True
        resource = self.loading_queue.pop(0)
        
        print(f"加载资源: {resource['id']} ({resource['type']})")
        
        # 根据资源类型使用不同的加载方法
        if resource['type'] == 'texture':
            self.load_texture(resource['path'], resource['id'])
        elif resource['type'] == 'model':
            self.load_model(resource['path'], resource['id'])
        elif resource['type'] == 'sound':
            self.load_sound(resource['path'], resource['id'])
        elif resource['type'] == 'data':
            self.load_data(resource['path'], resource['id'])
        else:
            print(f"未知资源类型: {resource['type']}")
            # 继续处理下一个资源
            self.process_loading_queue()
    
    def load_texture(self, path, texture_id):
        """加载纹理"""
        def on_texture_loaded(texture):
            self.resources[texture_id] = texture
            print(f"纹理加载完成: {texture_id}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        def on_texture_failed(error):
            print(f"纹理加载失败: {texture_id}, 错误: {error}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        # 使用资源加载器加载纹理
        self.loader.load_texture(path, on_texture_loaded, on_texture_failed)
    
    def load_model(self, path, model_id):
        """加载模型"""
        def on_model_loaded(model):
            self.resources[model_id] = model
            print(f"模型加载完成: {model_id}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        def on_model_failed(error):
            print(f"模型加载失败: {model_id}, 错误: {error}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        # 使用资源加载器加载模型
        self.loader.load_model(path, on_model_loaded, on_model_failed)
    
    def load_sound(self, path, sound_id):
        """加载声音"""
        def on_sound_loaded(sound):
            self.resources[sound_id] = sound
            print(f"声音加载完成: {sound_id}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        def on_sound_failed(error):
            print(f"声音加载失败: {sound_id}, 错误: {error}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        # 使用资源加载器加载声音
        self.loader.load_sound(path, on_sound_loaded, on_sound_failed)
    
    def load_data(self, path, data_id):
        """加载数据"""
        def on_data_loaded(data):
            self.resources[data_id] = data
            print(f"数据加载完成: {data_id}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        def on_data_failed(error):
            print(f"数据加载失败: {data_id}, 错误: {error}")
            
            # 继续处理下一个资源
            self.process_loading_queue()
        
        # 使用资源加载器加载数据
        self.loader.load_data(path, on_data_loaded, on_data_failed)
    
    def get_resource(self, resource_id):
        """获取资源"""
        if resource_id in self.resources:
            return self.resources[resource_id]
        else:
            print(f"资源未找到: {resource_id}")
            return None
    
    def unload_resource(self, resource_id):
        """卸载资源"""
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            
            # 根据资源类型使用不同的卸载方法
            if hasattr(resource, 'dispose'):
                resource.dispose()
            
            del self.resources[resource_id]
            print(f"资源已卸载: {resource_id}")
        else:
            print(f"资源未找到，无法卸载: {resource_id}")
    
    def unload_all_resources(self):
        """卸载所有资源"""
        resource_count = len(self.resources)
        
        for resource_id in list(self.resources.keys()):
            self.unload_resource(resource_id)
        
        print(f"已卸载所有 {resource_count} 个资源")
```

### 5. 服务端工具

```python
from ..architect.utils.server import ServerUtils

class GameServer:
    def __init__(self):
        self.utils = ServerUtils()
        self.players = {}
        self.game_state = "waiting"
    
    def start_server(self):
        """启动服务器"""
        server_info = self.utils.get_server_info()
        print(f"服务器版本: {server_info['version']}")
        print(f"服务器地址: {server_info['address']}")
        print(f"服务器端口: {server_info['port']}")
        print(f"最大玩家数: {server_info['max_players']}")
        
        # 启动网络服务
        self.utils.start_network_service()
        
        # 启动游戏循环
        self.start_game_loop()
    
    def handle_player_join(self, player_id, player_data):
        """处理玩家加入"""
        print(f"玩家加入: {player_id} ({player_data['name']})")
        
        # 添加玩家到列表
        self.players[player_id] = {
            'id': player_id,
            'name': player_data['name'],
            'level': player_data.get('level', 1),
            'position': [0, 0, 0],
            'health': 100,
            'connected': True,
            'join_time': self.utils.get_current_time()
        }
        
        # 广播玩家加入消息
        self.broadcast_message(f"玩家 {player_data['name']} 加入了游戏")
        
        # 发送欢迎消息给新玩家
        welcome_message = {
            'type': 'welcome',
            'message': f"欢迎来到游戏，{player_data['name']}!",
            'server_time': self.utils.get_current_time(),
            'player_count': len(self.players)
        }
        
        self.utils.send_to_player(player_id, welcome_message)
    
    def handle_player_leave(self, player_id):
        """处理玩家离开"""
        if player_id in self.players:
            player_name = self.players[player_id]['name']
            print(f"玩家离开: {player_id} ({player_name})")
            
            # 广播玩家离开消息
            self.broadcast_message(f"玩家 {player_name} 离开了游戏")
            
            # 从玩家列表中移除
            del self.players[player_id]
    
    def handle_player_message(self, player_id, message):
        """处理玩家消息"""
        if player_id not in self.players:
            return
        
        player_name = self.players[player_id]['name']
        
        if message['type'] == 'chat':
            # 处理聊天消息
            chat_message = message['text']
            print(f"聊天: {player_name}: {chat_message}")
            
            # 广播聊天消息
            self.broadcast_message(f"{player_name}: {chat_message}")
        
        elif message['type'] == 'move':
            # 处理移动消息
            position = message['position']
            self.players[player_id]['position'] = position
            
            # 广播位置更新给其他玩家
            position_update = {
                'type': 'position_update',
                'player_id': player_id,
                'position': position,
                'timestamp': self.utils.get_current_time()
            }
            
            self.broadcast_to_others(player_id, position_update)
        
        elif message['type'] == 'action':
            # 处理动作消息
            action = message['action']
            target = message.get('target')
            
            print(f"动作: {player_name} 执行了 {action}")
            
            # 处理不同的动作
            if action == 'attack':
                self.handle_attack(player_id, target)
            elif action == 'use_item':
                self.handle_use_item(player_id, target)
            elif action == 'interact':
                self.handle_interact(player_id, target)
    
    def broadcast_message(self, message):
        """广播消息给所有玩家"""
        broadcast_data = {
            'type': 'broadcast',
            'message': message,
            'timestamp': self.utils.get_current_time()
        }
        
        for player_id in self.players:
            self.utils.send_to_player(player_id, broadcast_data)
    
    def broadcast_to_others(self, exclude_player_id, data):
        """广播消息给除指定玩家外的所有玩家"""
        for player_id in self.players:
            if player_id != exclude_player_id:
                self.utils.send_to_player(player_id, data)
    
    def handle_attack(self, attacker_id, target_id):
        """处理攻击"""
        if attacker_id not in self.players or target_id not in self.players:
            return
        
        attacker = self.players[attacker_id]
        target = self.players[target_id]
        
        # 计算伤害
        damage = self.calculate_damage(attacker, target)
        
        # 应用伤害
        target['health'] -= damage
        
        print(f"攻击: {attacker['name']} 对 {target['name']} 造成了 {damage} 点伤害")
        
        # 广播攻击结果
        attack_result = {
            'type': 'attack_result',
            'attacker_id': attacker_id,
            'target_id': target_id,
            'damage': damage,
            'target_health': target['health']
        }
        
        self.broadcast_message(attack_result)
        
        # 检查目标是否死亡
        if target['health'] <= 0:
            self.handle_player_death(target_id, attacker_id)
    
    def calculate_damage(self, attacker, target):
        """计算伤害"""
        # 简单的伤害计算公式
        base_damage = 10
        level_bonus = (attacker['level'] - target['level']) * 2
        damage = max(1, base_damage + level_bonus)
        
        return damage
    
    def handle_player_death(self, player_id, killer_id):
        """处理玩家死亡"""
        player = self.players[player_id]
        killer = self.players.get(killer_id, {'name': '未知'})
        
        print(f"死亡: {player['name']} 被 {killer['name']} 击败")
        
        # 广播死亡消息
        death_message = {
            'type': 'player_death',
            'player_id': player_id,
            'killer_id': killer_id,
            'message': f"{player['name']} 被 {killer['name']} 击败了!"
        }
        
        self.broadcast_message(death_message)
        
        # 重置玩家状态
        player['health'] = 100
        player['position'] = [0, 0, 0]
        
        #