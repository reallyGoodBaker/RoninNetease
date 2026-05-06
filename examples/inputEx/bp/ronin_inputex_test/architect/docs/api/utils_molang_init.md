# MoLang工具 (Molang) API

`architect.utils.molang` 模块提供了Minecraft的MoLang表达式处理功能。MoLang是Minecraft中用于动画和渲染的表达式语言。

## 模块结构

`architect.utils.molang` 模块包含以下子模块：

- `architect.utils.molang.client` - 客户端MoLang工具
- `architect.utils.molang.common` - 通用MoLang工具
- `architect.utils.molang.server` - 服务端MoLang工具
- `architect.utils.molang.types` - MoLang类型定义

## MoLang简介

MoLang（Minecraft表达式语言）是一种用于Minecraft Bedrock Edition的简单表达式语言，主要用于：
- 实体动画
- 粒子效果
- 渲染参数
- 游戏逻辑计算

### 基本语法

```moLang
// 变量查询
query.is_on_ground
query.health
query.life_time

// 数学运算
math.sin(query.life_time * 1.23)
math.clamp(variable.x, 0, 1)

// 条件表达式
query.is_on_ground ? 0 : 1
variable.x > 0.5 ? 1 : 0
```

## 使用示例

### 1. 基本MoLang表达式处理

```python
class MoLangParser:
    """MoLang表达式解析器"""
    
    def __init__(self):
        self.variables = {}
        self.queries = {}
        self.functions = {}
        
        # 初始化内置函数
        self.init_builtin_functions()
    
    def init_builtin_functions(self):
        """初始化内置函数"""
        import math
        
        self.functions = {
            # 数学函数
            'math.sin': math.sin,
            'math.cos': math.cos,
            'math.tan': math.tan,
            'math.asin': math.asin,
            'math.acos': math.acos,
            'math.atan': math.atan,
            'math.atan2': math.atan2,
            'math.sqrt': math.sqrt,
            'math.abs': abs,
            'math.floor': math.floor,
            'math.ceil': math.ceil,
            'math.round': round,
            'math.trunc': math.trunc,
            'math.min': min,
            'math.max': max,
            'math.clamp': lambda x, min_val, max_val: max(min_val, min(x, max_val)),
            'math.lerp': lambda a, b, t: a + (b - a) * t,
            'math.lerprotate': lambda a, b, t: a + ((b - a + 180) % 360 - 180) * t,
            
            # 随机函数
            'math.random': lambda a, b: random.uniform(a, b) if a != b else a,
            'math.random_integer': lambda a, b: random.randint(int(a), int(b)),
            
            # 查询函数
            'query.anim_time': lambda: self.queries.get('anim_time', 0),
            'query.life_time': lambda: self.queries.get('life_time', 0),
            'query.health': lambda: self.queries.get('health', 1),
            'query.max_health': lambda: self.queries.get('max_health', 1),
            'query.is_on_ground': lambda: self.queries.get('is_on_ground', False),
            'query.is_in_water': lambda: self.queries.get('is_in_water', False),
            'query.is_on_fire': lambda: self.queries.get('is_on_fire', False),
            'query.yaw_speed': lambda: self.queries.get('yaw_speed', 0),
            'query.pitch_speed': lambda: self.queries.get('pitch_speed', 0),
        }
    
    def parse_expression(self, expression):
        """解析MoLang表达式"""
        # 简化解析：实际实现需要完整的语法解析
        try:
            # 替换变量
            for var_name, var_value in self.variables.items():
                expression = expression.replace(f'variable.{var_name}', str(var_value))
            
            # 替换查询
            for query_name, query_value in self.queries.items():
                expression = expression.replace(f'query.{query_name}', str(query_value))
            
            # 替换函数调用（简化）
            # 实际实现需要更复杂的解析
            
            # 评估表达式（简化）
            # 注意：实际实现应该使用安全的表达式求值
            result = self.evaluate_safe(expression)
            return result
            
        except Exception as e:
            print(f"解析表达式失败: {expression}, 错误: {e}")
            return 0
    
    def evaluate_safe(self, expression):
        """安全地评估表达式"""
        # 简化实现：使用Python的eval（实际生产环境应使用更安全的方法）
        # 这里仅用于演示
        
        # 创建安全的命名空间
        namespace = {
            'math': {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'sqrt': math.sqrt,
                'abs': abs,
                'min': min,
                'max': max,
            }
        }
        
        try:
            # 使用ast.literal_eval或自定义解析器更安全
            # 这里简化处理
            return eval(expression, {"__builtins__": {}}, namespace)
        except:
            return 0
    
    def set_variable(self, name, value):
        """设置变量"""
        self.variables[name] = value
    
    def get_variable(self, name):
        """获取变量"""
        return self.variables.get(name, 0)
    
    def set_query(self, name, value):
        """设置查询"""
        self.queries[name] = value
    
    def get_query(self, name):
        """获取查询"""
        return self.queries.get(name, 0)
    
    def register_function(self, name, func):
        """注册自定义函数"""
        self.functions[name] = func
    
    def test_expressions(self):
        """测试表达式"""
        test_cases = [
            ("1 + 2 * 3", 7),
            ("math.sin(0)", 0),
            ("math.cos(0)", 1),
            ("math.min(5, 10)", 5),
            ("math.max(5, 10)", 10),
            ("math.clamp(15, 0, 10)", 10),
            ("math.clamp(-5, 0, 10)", 0),
            ("math.clamp(5, 0, 10)", 5),
        ]
        
        results = []
        for expr, expected in test_cases:
            result = self.parse_expression(expr)
            success = abs(result - expected) < 0.0001
            results.append((expr, result, expected, success))
            
            status = "✓" if success else "✗"
            print(f"{status} {expr} = {result} (期望: {expected})")
        
        return results
```

### 2. 实体动画控制器

```python
class EntityAnimationController:
    """实体动画控制器"""
    
    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.parser = MoLangParser()
        self.animations = {}
        self.current_animation = None
        self.animation_time = 0
        self.animation_speed = 1.0
        
        # 初始化实体查询
        self.init_entity_queries()
    
    def init_entity_queries(self):
        """初始化实体查询"""
        # 设置默认查询值
        self.parser.set_query('life_time', 0)
        self.parser.set_query('health', 20)
        self.parser.set_query('max_health', 20)
        self.parser.set_query('is_on_ground', True)
        self.parser.set_query('is_in_water', False)
        self.parser.set_query('is_on_fire', False)
        self.parser.set_query('yaw_speed', 0)
        self.parser.set_query('pitch_speed', 0)
        self.parser.set_query('anim_time', 0)
    
    def register_animation(self, name, animation_def):
        """注册动画"""
        self.animations[name] = animation_def
        print(f"注册动画: {name}")
    
    def play_animation(self, name, speed=1.0, loop=False):
        """播放动画"""
        if name not in self.animations:
            print(f"动画未找到: {name}")
            return False
        
        self.current_animation = name
        self.animation_time = 0
        self.animation_speed = speed
        self.loop_animation = loop
        
        print(f"播放动画: {name}, 速度: {speed}, 循环: {loop}")
        return True
    
    def stop_animation(self):
        """停止动画"""
        if self.current_animation:
            print(f"停止动画: {self.current_animation}")
            self.current_animation = None
            self.animation_time = 0
            return True
        return False
    
    def update(self, delta_time):
        """更新动画"""
        if not self.current_animation:
            return
        
        # 更新动画时间
        self.animation_time += delta_time * self.animation_speed
        self.parser.set_query('anim_time', self.animation_time)
        
        # 获取动画定义
        animation_def = self.animations[self.current_animation]
        
        # 计算动画参数
        animation_params = self.calculate_animation_params(animation_def)
        
        # 应用动画参数到实体
        self.apply_animation_params(animation_params)
        
        # 检查动画是否结束
        if not self.loop_animation and self.animation_time >= animation_def.get('duration', 1.0):
            self.stop_animation()
    
    def calculate_animation_params(self, animation_def):
        """计算动画参数"""
        params = {}
        
        # 解析每个动画通道
        for channel_name, channel_def in animation_def.get('channels', {}).items():
            if 'expression' in channel_def:
                # 计算表达式值
                expression = channel_def['expression']
                value = self.parser.parse_expression(expression)
                params[channel_name] = value
            elif 'keyframes' in channel_def:
                # 关键帧动画
                value = self.calculate_keyframe_value(channel_def['keyframes'])
                params[channel_name] = value
        
        return params
    
    def calculate_keyframe_value(self, keyframes):
        """计算关键帧值"""
        if not keyframes:
            return 0
        
        # 查找当前时间所在的关键帧区间
        for i in range(len(keyframes) - 1):
            frame1 = keyframes[i]
            frame2 = keyframes[i + 1]
            
            time1, value1 = frame1['time'], frame1['value']
            time2, value2 = frame2['time'], frame2['value']
            
            if time1 <= self.animation_time <= time2:
                # 线性插值
                t = (self.animation_time - time1) / (time2 - time1)
                lerp_func = frame2.get('lerp_mode', 'linear')
                
                if lerp_func == 'linear':
                    return value1 + (value2 - value1) * t
                elif lerp_func == 'step':
                    return value1
                elif lerp_func == 'catmullrom':
                    # Catmull-Rom样条插值（简化）
                    return self.catmull_rom_interpolation(t, value1, value2)
        
        # 如果时间超出范围，返回最后一个关键帧的值
        return keyframes[-1]['value']
    
    def catmull_rom_interpolation(self, t, p1, p2):
        """Catmull-Rom样条插值（简化）"""
        # 简化实现：实际需要4个点
        return p1 + (p2 - p1) * t
    
    def apply_animation_params(self, params):
        """应用动画参数到实体"""
        # 这里应该将参数应用到实际的实体
        # 例如：设置实体的位置、旋转、缩放等
        
        for param_name, param_value in params.items():
            # 根据参数名称应用到不同的实体属性
            if param_name.startswith('position.'):
                axis = param_name.split('.')[1]
                # 设置位置
                pass
            elif param_name.startswith('rotation.'):
                axis = param_name.split('.')[1]
                # 设置旋转
                pass
            elif param_name.startswith('scale.'):
                axis = param_name.split('.')[1]
                # 设置缩放
                pass
        
        # 打印调试信息
        if params:
            print(f"动画参数: {params}")
    
    def create_walk_animation(self):
        """创建行走动画"""
        walk_animation = {
            'name': 'walk',
            'duration': 1.0,
            'channels': {
                'position.y': {
                    'expression': 'math.sin(query.anim_time * 6.28) * 0.1'
                },
                'rotation.x': {
                    'expression': 'math.sin(query.anim_time * 6.28) * 5'
                },
                'rotation.z': {
                    'expression': 'math.cos(query.anim_time * 6.28) * 3'
                }
            }
        }
        
        self.register_animation('walk', walk_animation)
        return walk_animation
    
    def create_idle_animation(self):
        """创建空闲动画"""
        idle_animation = {
            'name': 'idle',
            'duration': 2.0,
            'channels': {
                'position.y': {
                    'expression': 'math.sin(query.anim_time * 3.14) * 0.05'
                },
                'rotation.y': {
                    'keyframes': [
                        {'time': 0.0, 'value': 0, 'lerp_mode': 'linear'},
                        {'time': 1.0, 'value': 10, 'lerp_mode': 'linear'},
                        {'time': 2.0, 'value': 0, 'lerp_mode': 'linear'}
                    ]
                }
            }
        }
        
        self.register_animation('idle', idle_animation)
        return idle_animation
    
    def create_jump_animation(self):
        """创建跳跃动画"""
        jump_animation = {
            'name': 'jump',
            'duration': 1.5,
            'channels': {
                'position.y': {
                    'keyframes': [
                        {'time': 0.0, 'value': 0, 'lerp_mode': 'linear'},
                        {'time': 0.3, 'value': 1, 'lerp_mode': 'linear'},
                        {'time': 0.8, 'value': 0.5, 'lerp_mode': 'linear'},
                        {'time': 1.5, 'value': 0, 'lerp_mode': 'linear'}
                    ]
                },
                'scale.y': {
                    'expression': '1.0 + math.sin(query.anim_time * 3.14) * 0.1'
                }
            }
        }
        
        self.register_animation('jump', jump_animation)
        return jump_animation
```

### 3. 粒子效果控制器

```python
class ParticleEffectController:
    """粒子效果控制器"""
    
    def __init__(self):
        self.parser = MoLangParser()
        self.particle_systems = {}
        self.active_particles = []
        
        # 初始化粒子查询
        self.init_particle_queries()
    
    def init_particle_queries(self):
        """初始化粒子查询"""
        self.parser.set_query('particle_age', 0)
        self.parser.set_query('particle_lifetime', 1)
        self.parser.set_query('particle_random_1', random.random())
        self.parser.set_query('particle_random_2', random.random())
        self.parser.set_query('particle_random_3', random.random())
        self.parser.set_query('particle_random_4', random.random())
    
    def create_particle_system(self, name, particle_def):
        """创建粒子系统"""
        self.particle_systems[name] = particle_def
        print(f"创建粒子系统: {name}")
        return particle_def
    
    def emit_particle(self, system_name, position, count=1):
        """发射粒子"""
        if system_name not in self.particle_systems:
            print(f"粒子系统未找到: {system_name}")
            return []
        
        particle_def = self.particle_systems[system_name]
        new_particles = []
        
        for i in range(count):
            particle = {
                'id': len(self.active_particles) + i,
                'system': system_name,
                'position': list(position),
                'velocity': [0, 0, 0],
                'age': 0,
                'lifetime': particle_def.get('lifetime', 1.0),
                'size': particle_def.get('initial_size', 1.0),
                'color': particle_def.get('initial_color', [1, 1, 1, 1]),
                'rotation': 0,
                'custom_data': {}
            }
            
            # 应用初始表达式
            self.apply_particle_expressions(particle, particle_def, 'initial')
            
            new_particles.append(particle)
        
        self.active_particles.extend(new_particles)
        print(f"发射 {count} 个粒子: {system_name}")
        
        return new_particles
    
    def update_particles(self, delta_time):
        """更新所有粒子"""
        particles_to_remove = []
        
        for particle in self.active_particles:
            # 更新粒子年龄
            particle['age'] += delta_time
            
            # 设置查询值
            self.parser.set_query('particle_age', particle['age'])
            self.parser.set_query('particle_lifetime', particle['lifetime'])
            
            # 获取粒子定义
            system_name = particle['system']
            if system_name in self.particle_systems:
                particle_def = self.particle_systems[system_name]
                
                # 应用更新表达式
                self.apply_particle_expressions(particle, particle_def, 'update')
                
                # 更新