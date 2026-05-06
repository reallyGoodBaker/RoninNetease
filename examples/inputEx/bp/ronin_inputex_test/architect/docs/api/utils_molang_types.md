# MoLang类型定义 (MolangTypes) API

`architect.utils.molang.types` 模块定义了MoLang相关的基础类型接口，包括可读接口和可变接口。

## 类

### `MolangReadable`

MoLang可读接口，定义了获取MoLang值的方法。

#### 方法

##### `getValue(actorId, defaultValue)`

获取MoLang值。

- **`actorId`**: 实体ID
- **`defaultValue`**: 默认值（当无法获取值时返回）
- **返回值**: MoLang值
- **注意**: 这是一个抽象方法，需要在子类中实现

### `MolangMutable`

MoLang可变接口，继承自 `MolangReadable`，定义了设置MoLang值的方法。

#### 方法

##### `setValue(actorId, value)`

设置MoLang值。

- **`actorId`**: 实体ID
- **`value`**: 要设置的值
- **注意**: 这是一个抽象方法，需要在子类中实现

## 使用示例

### 1. 基础接口实现

```python
from ..architect.utils.molang.types import MolangReadable, MolangMutable

class SimpleMoLangVariable(MolangMutable):
    """简单的MoLang变量实现"""
    
    def __init__(self, name, default_value=0):
        self.name = name
        self.default_value = default_value
        self.values = {}  # 存储实体值: {actor_id: value}
    
    def getValue(self, actorId, defaultValue=None):
        """获取值"""
        if defaultValue is None:
            defaultValue = self.default_value
        
        # 从存储中获取值
        return self.values.get(actorId, defaultValue)
    
    def setValue(self, actorId, value):
        """设置值"""
        self.values[actorId] = value
        print(f"设置实体 {actorId} 的变量 {self.name} = {value}")
        return True

class CalculatedMoLangVariable(MolangReadable):
    """计算型MoLang变量"""
    
    def __init__(self, name, calculation_func):
        self.name = name
        self.calculation_func = calculation_func
    
    def getValue(self, actorId, defaultValue=0):
        """获取计算值"""
        try:
            # 调用计算函数
            return self.calculation_func(actorId)
        except Exception as e:
            print(f"计算变量 {self.name} 时出错: {e}")
            return defaultValue

class CompositeMoLangVariable(MolangMutable):
    """组合型MoLang变量"""
    
    def __init__(self, name):
        self.name = name
        self.sources = []  # 数据源列表
        self.transform_func = None  # 转换函数
    
    def add_source(self, source):
        """添加数据源"""
        if isinstance(source, MolangReadable):
            self.sources.append(source)
            return True
        return False
    
    def set_transform(self, transform_func):
        """设置转换函数"""
        self.transform_func = transform_func
    
    def getValue(self, actorId, defaultValue=0):
        """获取组合值"""
        if not self.sources:
            return defaultValue
        
        # 收集所有源的值
        values = []
        for source in self.sources:
            try:
                value = source.getValue(actorId, defaultValue)
                values.append(value)
            except:
                values.append(defaultValue)
        
        # 应用转换函数
        if self.transform_func:
            try:
                return self.transform_func(values)
            except:
                pass
        
        # 默认：返回平均值
        if values:
            return sum(values) / len(values)
        
        return defaultValue
    
    def setValue(self, actorId, value):
        """设置值（分发到所有可变源）"""
        success_count = 0
        
        for source in self.sources:
            if isinstance(source, MolangMutable):
                try:
                    source.setValue(actorId, value)
                    success_count += 1
                except:
                    pass
        
        print(f"设置组合变量 {self.name}: 成功更新 {success_count}/{len(self.sources)} 个源")
        return success_count > 0
```

### 2. 类型检查和工厂模式

```python
from ..architect.utils.molang.types import MolangReadable, MolangMutable

class MoLangTypeFactory:
    """MoLang类型工厂"""
    
    @staticmethod
    def create_readonly_variable(name, value_provider):
        """创建只读变量"""
        class ReadOnlyVariable(MolangReadable):
            def getValue(self, actorId, defaultValue=0):
                try:
                    return value_provider(actorId)
                except:
                    return defaultValue
        
        variable = ReadOnlyVariable()
        variable.name = name
        return variable
    
    @staticmethod
    def create_writable_variable(name, initial_value=0):
        """创建可写变量"""
        class WritableVariable(MolangMutable):
            def __init__(self):
                self.values = {}
                self.default_value = initial_value
            
            def getValue(self, actorId, defaultValue=None):
                if defaultValue is None:
                    defaultValue = self.default_value
                return self.values.get(actorId, defaultValue)
            
            def setValue(self, actorId, value):
                self.values[actorId] = value
                return True
        
        variable = WritableVariable()
        variable.name = name
        return variable
    
    @staticmethod
    def create_cached_variable(name, source_variable, cache_duration=1.0):
        """创建缓存变量"""
        class CachedVariable(MolangReadable):
            def __init__(self):
                self.cache = {}
                self.cache_times = {}
                self.cache_duration = cache_duration
            
            def getValue(self, actorId, defaultValue=0):
                current_time = time.time()
                
                # 检查缓存是否有效
                if (actorId in self.cache and 
                    actorId in self.cache_times and
                    current_time - self.cache_times[actorId] < self.cache_duration):
                    return self.cache[actorId]
                
                # 从源获取值
                try:
                    value = source_variable.getValue(actorId, defaultValue)
                    self.cache[actorId] = value
                    self.cache_times[actorId] = current_time
                    return value
                except:
                    return defaultValue
        
        variable = CachedVariable()
        variable.name = name
        variable.source = source_variable
        return variable
    
    @staticmethod
    def create_validated_variable(name, source_variable, validation_func):
        """创建验证变量"""
        class ValidatedVariable(MolangMutable):
            def __init__(self):
                self.source = source_variable
                self.validation_func = validation_func
            
            def getValue(self, actorId, defaultValue=0):
                return self.source.getValue(actorId, defaultValue)
            
            def setValue(self, actorId, value):
                # 验证值
                if self.validation_func(value):
                    if isinstance(self.source, MolangMutable):
                        return self.source.setValue(actorId, value)
                    else:
                        print(f"错误: 源变量 {name} 不可写")
                        return False
                else:
                    print(f"验证失败: 值 {value} 无效")
                    return False
        
        variable = ValidatedVariable()
        variable.name = name
        return variable

class MoLangTypeChecker:
    """MoLang类型检查器"""
    
    @staticmethod
    def is_molang_readable(obj):
        """检查对象是否可读"""
        return isinstance(obj, MolangReadable)
    
    @staticmethod
    def is_molang_mutable(obj):
        """检查对象是否可变"""
        return isinstance(obj, MolangMutable)
    
    @staticmethod
    def ensure_readable(obj, default_value_provider=None):
        """确保对象可读"""
        if MoLangTypeChecker.is_molang_readable(obj):
            return obj
        
        # 如果不是MolangReadable，尝试包装
        if callable(obj):
            # 如果是函数，创建只读变量
            return MoLangTypeFactory.create_readonly_variable("wrapped", obj)
        elif default_value_provider is not None:
            # 使用默认值提供器
            return MoLangTypeFactory.create_readonly_variable("wrapped", default_value_provider)
        else:
            # 创建常量变量
            return MoLangTypeFactory.create_readonly_variable("constant", lambda actorId: obj)
    
    @staticmethod
    def ensure_mutable(obj, initial_value=0):
        """确保对象可变"""
        if MoLangTypeChecker.is_molang_mutable(obj):
            return obj
        
        # 如果不是MolangMutable，创建可写变量
        return MoLangTypeFactory.create_writable_variable("wrapped_mutable", initial_value)
    
    @staticmethod
    def get_value_safely(variable, actorId, default=0):
        """安全地获取值"""
        if MoLangTypeChecker.is_molang_readable(variable):
            try:
                return variable.getValue(actorId, default)
            except:
                return default
        else:
            return default
    
    @staticmethod
    def set_value_safely(variable, actorId, value):
        """安全地设置值"""
        if MoLangTypeChecker.is_molang_mutable(variable):
            try:
                return variable.setValue(actorId, value)
            except Exception as e:
                print(f"设置值时出错: {e}")
                return False
        else:
            print(f"错误: 变量不可写")
            return False
```

### 3. 高级类型系统

```python
from ..architect.utils.molang.types import MolangReadable, MolangMutable
import time

class MoLangTypeSystem:
    """MoLang类型系统"""
    
    def __init__(self):
        self.registered_types = {}
        self.type_adapters = {}
        
        self.register_builtin_types()
    
    def register_builtin_types(self):
        """注册内置类型"""
        # 注册基础类型
        self.register_type('constant', self.create_constant_type)
        self.register_type('calculated', self.create_calculated_type)
        self.register_type('cached', self.create_cached_type)
        self.register_type('validated', self.create_validated_type)
        
        # 注册类型适配器
        self.register_adapter(int, self.adapt_int_to_molang)
        self.register_adapter(float, self.adapt_float_to_molang)
        self.register_adapter(bool, self.adapt_bool_to_molang)
        self.register_adapter(str, self.adapt_str_to_molang)
        self.register_adapter(type(None), self.adapt_none_to_molang)
    
    def register_type(self, type_name, type_creator):
        """注册类型"""
        self.registered_types[type_name] = type_creator
    
    def register_adapter(self, source_type, adapter_func):
        """注册类型适配器"""
        self.type_adapters[source_type] = adapter_func
    
    def create_constant_type(self, value):
        """创建常量类型"""
        class ConstantVariable(MolangReadable):
            def getValue(self, actorId, defaultValue=None):
                return value
        
        return ConstantVariable()
    
    def create_calculated_type(self, calculation_func):
        """创建计算类型"""
        class CalculatedVariable(MolangReadable):
            def getValue(self, actorId, defaultValue=0):
                try:
                    return calculation_func(actorId)
                except:
                    return defaultValue
        
        return CalculatedVariable()
    
    def create_cached_type(self, source_variable, cache_time=1.0):
        """创建缓存类型"""
        class CachedVariable(MolangReadable):
            def __init__(self):
                self.cache = {}
                self.cache_time = {}
                self.source = source_variable
                self.cache_duration = cache_time
            
            def getValue(self, actorId, defaultValue=0):
                current_time = time.time()
                
                # 检查缓存
                if (actorId in self.cache and 
                    actorId in self.cache_time and
                    current_time - self.cache_time[actorId] < self.cache_duration):
                    return self.cache[actorId]
                
                # 从源获取
                try:
                    value = self.source.getValue(actorId, defaultValue)
                    self.cache[actorId] = value
                    self.cache_time[actorId] = current_time
                    return value
                except:
                    return defaultValue
        
        return CachedVariable()
    
    def create_validated_type(self, source_variable, validation_func):
        """创建验证类型"""
        if not isinstance(source_variable, MolangMutable):
            # 如果源不可变，创建包装器
            source_variable = self.ensure_mutable(source_variable)
        
        class ValidatedVariable(MolangMutable):
            def __init__(self):
                self.source = source_variable
                self.validation_func = validation_func
            
            def getValue(self, actorId, defaultValue=0):
                return self.source.getValue(actorId, defaultValue)
            
            def setValue(self, actorId, value):
                if self.validation_func(value):
                    return self.source.setValue(actorId, value)
                else:
                    print(f"验证失败: 值 {value} 无效")
                    return False
        
        return ValidatedVariable()
    
    def adapt_int_to_molang(self, value):
        """适配整数到MoLang"""
        return self.create_constant_type(float(value))
    
    def adapt_float_to_molang(self, value):
        """适配浮点数到MoLang"""
        return self.create_constant_type(value)
    
    def adapt_bool_to_molang(self, value):
        """适配布尔值到MoLang"""
        return self.create_constant_type(1.0 if value else 0.0)
    
    def adapt_str_to_molang(self, value):
        """适配字符串到MoLang"""
        # 尝试转换为数字
        try:
            return self.create_constant_type(float(value))
        except:
            # 如果无法转换，使用字符串哈希
            return self.create_constant_type(float(hash(value) % 1000))
    
    def adapt_none_to_molang(self, value):
        """适配None到MoLang"""
        return self.create_constant_type(0.0)
    
    def adapt_to_molang(self, value):
        """适配任意值到MoLang"""
        # 检查是否已经是MoLang类型
        if isinstance(value, MolangReadable):
            return value
        
        # 查找适配器
        value_type = type(value)
        
        # 检查精确类型匹配
        if value_type in self.type_adapters:
            return self.type_adapters[value_type](value)
        
        # 检查父类匹配
        for source_type, adapter in self.type_adapters.items():
            if isinstance(value, source_type):
                return adapter(value)
        
        # 默认适配器
        return self.create_constant_type(float(value) if isinstance(value, (int, float)) else 0.0)
    
    def ensure_mutable(self, variable):
        """确保变量可变"""
        if isinstance(variable, MolangMutable):
            return variable
        
        # 如果不是可变类型，创建包装器
        class MutableWrapper(MolangMutable):
            def __init__(self, source):
                self.source = self.adapt_to_molang(source)
                self.values = {}
            
            def getValue(self, actorId, defaultValue=0):
                # 首先检查本地存储的值
                if actorId in self.values:
                    return self.values[actorId]
                
                # 然后从源获取
                return self.source.getValue(actorId, defaultValue)
            
            def setValue(self, actorId, value):
                self.values[actorId] = value
                return True
        
        return MutableWrapper(variable)
    
    def create_composite_variable(self, name, *sources, combine_func=None):
        """创建组合变量"""
        # 适配所有源
        adapted_sources = [self.adapt_to_molang(source) for source in sources]
        
        class CompositeVariable(MolangReadable):
            def getValue(self, actorId, defaultValue=0):
                values = []
                for source in adapted_sources:
                    try:
                        value = source.getValue(actorId, defaultValue)
                        values.append(value)
                    except:
                        values.append(defaultValue)
                
                if combine_func:
                    try:
                        return combine_func(values)
                    except:
                        pass
                
                # 默认：返回平均值
                if values:
                    return sum(values) / len(values)
                
                return defaultValue
        
        variable = CompositeVariable()
        variable.name = name
        variable.sources = adapted_sources
        return variable
    
    def create_conditional_variable(self, name, condition, true_value, false_value):
        """创建条件变量"""
        # 适配所有值
        condition_var = self.adapt_to_molang(condition)
        true_var = self.adapt_to_molang(true_value)
        false_var = self.adapt_to_molang(false_value)
        
        class ConditionalVariable(MolangReadable):
            def getValue(self, actorId, defaultValue=0):
                try:
                    cond_value = condition_var.getValue(actorId, 0)
                    
                    # 检查条件是否为真（非零值视为真）
                    if cond_value:
                        return true_var.getValue(actorId, defaultValue)
                    else:
                        return false_var.getValue(actorId, defaultValue)
                except:
                    return defaultValue
        
        variable = ConditionalVariable()
        variable.name = name
        return variable
    
    def test_type_system(self):
        """测试类型系统"""
        print("=== MoLang类型系统测试 ===")
        
        # 测试常量类型
        constant_var = self.create_constant_type(42.5)
        print(f"常量变量值: {constant_var.getValue(1, 0)}")
        
        # 测试计算类型
        calc_var = self.create_calculated_type(lambda actorId: actorId * 10)
        print(f"计算变量值 (actorId=5): {calc_var.getValue(5, 0)}")
        
        # 测试适配器
        int_var = self.adapt_to_molang(100)
        print(f"整数适配值: {int_var.getValue(1, 0)}")
        
        bool_var = self.adapt_to_molang(True)
        print(f"布尔适配值: {bool_var.getValue(1, 0)}")
        
        str_var = self.adapt_to_molang("test")
        print(f"字符串适配值: {str_var.getValue(1, 0)}")
        
        # 测试组合变量
        composite_var = self.create_composite_variable(
            "composite",
            10, 20,