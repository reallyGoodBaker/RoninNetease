# 增强工具 (Enhance) API

`architect.utils.enhance` 模块提供了增强功能工具，用于扩展和增强Python内置数据类型的功能。

## 模块结构

`architect.utils.enhance` 模块包含以下子模块：

- `architect.utils.enhance.list` - 增强列表功能

## 使用示例

### 1. 增强列表类

```python
class EnhancedList(list):
    """增强列表类，扩展了标准列表的功能"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []  # 操作历史记录
    
    def add(self, item):
        """添加元素到列表末尾"""
        self.append(item)
        self.history.append(('add', item, len(self)-1))
        return self
    
    def insert_at(self, index, item):
        """在指定位置插入元素"""
        self.insert(index, item)
        self.history.append(('insert', item, index))
        return self
    
    def remove_item(self, item):
        """移除指定元素"""
        if item in self:
            index = self.index(item)
            self.remove(item)
            self.history.append(('remove', item, index))
            return True
        return False
    
    def remove_at(self, index):
        """移除指定位置的元素"""
        if 0 <= index < len(self):
            item = self[index]
            del self[index]
            self.history.append(('remove_at', item, index))
            return item
        raise IndexError("索引超出范围")
    
    def get_first(self):
        """获取第一个元素"""
        return self[0] if self else None
    
    def get_last(self):
        """获取最后一个元素"""
        return self[-1] if self else None
    
    def get_random(self):
        """随机获取一个元素"""
        import random
        return random.choice(self) if self else None
    
    def shuffle(self):
        """随机打乱列表"""
        import random
        random.shuffle(self)
        self.history.append(('shuffle', None, None))
        return self
    
    def clear_all(self):
        """清空列表"""
        items = list(self)
        self.clear()
        self.history.append(('clear_all', items, None))
        return items
    
    def filter(self, condition):
        """过滤列表元素"""
        filtered = EnhancedList(item for item in self if condition(item))
        self.history.append(('filter', condition, len(filtered)))
        return filtered
    
    def map(self, func):
        """映射列表元素"""
        mapped = EnhancedList(func(item) for item in self)
        self.history.append(('map', func, len(mapped)))
        return mapped
    
    def reduce(self, func, initial=None):
        """归约列表元素"""
        from functools import reduce
        if initial is not None:
            result = reduce(func, self, initial)
        else:
            result = reduce(func, self)
        self.history.append(('reduce', func, result))
        return result
    
    def group_by(self, key_func):
        """按键函数分组"""
        groups = {}
        for item in self:
            key = key_func(item)
            if key not in groups:
                groups[key] = EnhancedList()
            groups[key].append(item)
        self.history.append(('group_by', key_func, len(groups)))
        return groups
    
    def chunk(self, size):
        """将列表分块"""
        chunks = []
        for i in range(0, len(self), size):
            chunks.append(EnhancedList(self[i:i+size]))
        self.history.append(('chunk', size, len(chunks)))
        return EnhancedList(chunks)
    
    def flatten(self):
        """展平嵌套列表"""
        flattened = EnhancedList()
        for item in self:
            if isinstance(item, (list, EnhancedList)):
                flattened.extend(item.flatten() if isinstance(item, EnhancedList) else item)
            else:
                flattened.append(item)
        self.history.append(('flatten', None, len(flattened)))
        return flattened
    
    def unique(self):
        """去重"""
        unique_list = EnhancedList()
        seen = set()
        for item in self:
            if item not in seen:
                seen.add(item)
                unique_list.append(item)
        self.history.append(('unique', None, len(unique_list)))
        return unique_list
    
    def sort_by(self, key_func=None, reverse=False):
        """按键函数排序"""
        sorted_list = EnhancedList(sorted(self, key=key_func, reverse=reverse))
        self.history.append(('sort_by', key_func, reverse))
        return sorted_list
    
    def reverse_list(self):
        """反转列表"""
        reversed_list = EnhancedList(reversed(self))
        self.history.append(('reverse', None, None))
        return reversed_list
    
    def get_history(self):
        """获取操作历史"""
        return self.history
    
    def undo_last(self):
        """撤销最后一次操作"""
        if not self.history:
            return False
        
        last_op = self.history.pop()
        op_type, item, index = last_op
        
        if op_type == 'add':
            self.pop()
        elif op_type == 'insert':
            del self[index]
        elif op_type == 'remove':
            self.insert(index, item)
        elif op_type == 'remove_at':
            self.insert(index, item)
        elif op_type == 'clear_all':
            self.extend(item)
        # 注意：其他操作可能无法完全撤销
        
        return True
    
    def to_dict(self, key_func=None, value_func=None):
        """转换为字典"""
        result = {}
        for item in self:
            if key_func:
                key = key_func(item)
            else:
                key = item
            
            if value_func:
                value = value_func(item)
            else:
                value = item
            
            result[key] = value
        
        return result
    
    def to_set(self):
        """转换为集合"""
        return set(self)
    
    def to_tuple(self):
        """转换为元组"""
        return tuple(self)
    
    def count_by(self, condition):
        """按条件计数"""
        count = 0
        for item in self:
            if condition(item):
                count += 1
        return count
    
    def any_match(self, condition):
        """检查是否有元素满足条件"""
        for item in self:
            if condition(item):
                return True
        return False
    
    def all_match(self, condition):
        """检查是否所有元素都满足条件"""
        for item in self:
            if not condition(item):
                return False
        return True
    
    def find_first(self, condition):
        """查找第一个满足条件的元素"""
        for item in self:
            if condition(item):
                return item
        return None
    
    def find_all(self, condition):
        """查找所有满足条件的元素"""
        return EnhancedList(item for item in self if condition(item))
    
    def find_index(self, condition):
        """查找第一个满足条件的元素的索引"""
        for i, item in enumerate(self):
            if condition(item):
                return i
        return -1
    
    def find_indices(self, condition):
        """查找所有满足条件的元素的索引"""
        return EnhancedList(i for i, item in enumerate(self) if condition(item))
    
    def replace(self, old_item, new_item):
        """替换元素"""
        indices = self.find_indices(lambda x: x == old_item)
        for index in indices:
            self[index] = new_item
        
        if indices:
            self.history.append(('replace', (old_item, new_item), len(indices)))
        
        return len(indices)
    
    def replace_at(self, index, new_item):
        """替换指定位置的元素"""
        if 0 <= index < len(self):
            old_item = self[index]
            self[index] = new_item
            self.history.append(('replace_at', (old_item, new_item), index))
            return old_item
        raise IndexError("索引超出范围")
    
    def swap(self, index1, index2):
        """交换两个位置的元素"""
        if 0 <= index1 < len(self) and 0 <= index2 < len(self):
            self[index1], self[index2] = self[index2], self[index1]
            self.history.append(('swap', (index1, index2), None))
            return True
        return False
    
    def rotate(self, n):
        """旋转列表"""
        if not self:
            return self
        
        n = n % len(self)
        rotated = EnhancedList(self[-n:] + self[:-n])
        self.history.append(('rotate', n, None))
        return rotated
    
    def get_slice(self, start=None, end=None, step=None):
        """获取切片"""
        return EnhancedList(self[start:end:step])
    
    def batch_process(self, batch_size, process_func):
        """批量处理"""
        results = EnhancedList()
        for i in range(0, len(self), batch_size):
            batch = EnhancedList(self[i:i+batch_size])
            result = process_func(batch)
            results.append(result)
        return results
    
    def print_items(self, separator=", "):
        """打印列表元素"""
        print(separator.join(str(item) for item in self))
    
    def save_to_file(self, filename):
        """保存到文件"""
        with open(filename, 'w') as f:
            for item in self:
                f.write(str(item) + '\n')
        self.history.append(('save_to_file', filename, len(self)))
    
    def load_from_file(self, filename):
        """从文件加载"""
        with open(filename, 'r') as f:
            lines = f.readlines()
            self.clear()
            self.extend(line.strip() for line in lines)
        self.history.append(('load_from_file', filename, len(self)))
```

### 2. 增强字典类

```python
class EnhancedDict(dict):
    """增强字典类，扩展了标准字典的功能"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []  # 操作历史记录
    
    def get_or_default(self, key, default=None):
        """获取值，如果键不存在则返回默认值"""
        return self.get(key, default)
    
    def get_or_set(self, key, default):
        """获取值，如果键不存在则设置默认值并返回"""
        if key not in self:
            self[key] = default
            self.history.append(('get_or_set', key, default))
        return self[key]
    
    def set_default(self, key, default):
        """设置默认值（如果键不存在）"""
        if key not in self:
            self[key] = default
            self.history.append(('set_default', key, default))
            return default
        return self[key]
    
    def update_many(self, items):
        """批量更新"""
        for key, value in items:
            self[key] = value
        self.history.append(('update_many', items, len(items)))
    
    def remove_key(self, key):
        """移除键"""
        if key in self:
            value = self[key]
            del self[key]
            self.history.append(('remove_key', key, value))
            return value
        return None
    
    def filter_keys(self, condition):
        """过滤键"""
        filtered = EnhancedDict()
        for key, value in self.items():
            if condition(key):
                filtered[key] = value
        self.history.append(('filter_keys', condition, len(filtered)))
        return filtered
    
    def filter_values(self, condition):
        """过滤值"""
        filtered = EnhancedDict()
        for key, value in self.items():
            if condition(value):
                filtered[key] = value
        self.history.append(('filter_values', condition, len(filtered)))
        return filtered
    
    def map_keys(self, func):
        """映射键"""
        mapped = EnhancedDict()
        for key, value in self.items():
            new_key = func(key)
            mapped[new_key] = value
        self.history.append(('map_keys', func, len(mapped)))
        return mapped
    
    def map_values(self, func):
        """映射值"""
        mapped = EnhancedDict()
        for key, value in self.items():
            mapped[key] = func(value)
        self.history.append(('map_values', func, len(mapped)))
        return mapped
    
    def invert(self):
        """反转键值对"""
        inverted = EnhancedDict()
        for key, value in self.items():
            inverted[value] = key
        self.history.append(('invert', None, len(inverted)))
        return inverted
    
    def merge(self, other_dict, conflict_resolver=None):
        """合并字典"""
        merged = EnhancedDict(self)
        for key, value in other_dict.items():
            if key in merged and conflict_resolver:
                merged[key] = conflict_resolver(merged[key], value)
            else:
                merged[key] = value
        self.history.append(('merge', other_dict, len(merged)))
        return merged
    
    def deep_merge(self, other_dict, conflict_resolver=None):
        """深度合并字典"""
        def merge_dicts(dict1, dict2):
            result = EnhancedDict(dict1)
            for key, value in dict2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                elif key in result and conflict_resolver:
                    result[key] = conflict_resolver(result[key], value)
                else:
                    result[key] = value
            return result
        
        merged = merge_dicts(self, other_dict)
        self.history.append(('deep_merge', other_dict, len(merged)))
        return merged
    
    def flatten(self, separator='.'):
        """展平嵌套字典"""
        def flatten_dict(d, parent_key=''):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                else:
                    items.append((new_key, v))
            return EnhancedDict(items)
        
        flattened = flatten_dict(self)
        self.history.append(('flatten', separator, len(flattened)))
        return flattened
    
    def group_by(self, key_func):
        """按键函数分组"""
        groups = EnhancedDict()
        for key, value in self.items():
            group_key = key_func(key, value)
            if group_key not in groups:
                groups[group_key] = EnhancedList()
            groups[group_key].append((key, value))
        self.history.append(('group_by', key_func, len(groups)))
        return groups
    
    def sort_by_key(self, reverse=False):
        """按键排序"""
        sorted_items = sorted(self.items(), key=lambda x: x[0], reverse=reverse)
        sorted_dict = EnhancedDict(sorted_items)
        self.history.append(('sort_by_key', reverse, len(sorted_dict)))
        return sorted_dict
    
    def sort_by_value(self, reverse=False):
        """按值排序"""
        sorted_items = sorted(self.items(), key=lambda x: x[1], reverse=reverse)
        sorted_dict = EnhancedDict(sorted_items)
        self.history.append(('sort_by_value', reverse, len(sorted_dict)))
        return sorted_dict
    
    def get_keys(self):
        """获取所有键"""
        return EnhancedList(self.keys())
    
    def get_values(self):
        """获取所有值"""
        return EnhancedList(self.values())
    
    def get_items(self):
        """获取所有键值对"""
        return EnhancedList(self.items())
    
    def find_key(self, condition):
        """查找满足条件的键"""
        for key in self.keys():
            if condition(key):
                return key
        return None
    
    def find_value(self, condition):
        """查找满足条件的值"""
        for value in self.values():
            if condition(value):
                return value
        return None
    
    def find_item(self, condition):
        """查找满足条件的键值对"""
        for key, value in self.items():
            if condition(key, value):
                return (key, value)
        return None
    
    def transform(self, transformer):
        """转换字典"""
        transformed = EnhancedDict()
        for key, value in self.items():
            new_key, new_value = transformer(key, value)
            transformed[new_key] = new_value
        self.history.append(('transform', transformer, len(transformed)))
        return transformed
    
    def to_list(self, item_formatter=None):
        """转换为列表"""
        if item_formatter:
            return EnhancedList(item_formatter(key, value) for key, value in self.items())
        else:
            return EnhancedList(self.items())
    
    def to_json(self):
        """转换为JSON字符串"""
        import json
        return json.dumps(self)
    
    def from_json(self, json_str):
        """从JSON字符串加载"""
        import json
        data = json.loads(json_str)
        self.clear()
        self.update(data)
        self.history.append(('from_json', json_str, len(self)))
    
    def save_to_file(self, filename):
        """保存到文件"""
        import json
        with open(filename, 'w') as f:
            json.dump(self, f, indent=2)
        self.history.append(('save_to_file', filename, len(self)))
    
    def load_from_file(self, filename):
        """从文件加载"""
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        self.clear()
        self.update(data)
        self.history.append(('load_from_file', filename, len(self)))
    
    def print_items(self, separator=": "):
        """打印字典项"""
        for key, value in self.items():
            print(f"{key}{separator}{value}")
```

### 3. 增强集合类

```python
class EnhancedSet(set):
    """增强集合类，扩展了标准集合的功能"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []  # 操作历史记录
    
    def add_many(self, items):
        """添加多个元素"""
        for item in items:
            self.add(item)
        self.history.append(('add_many', items, len(items)))
    
    def remove_many(self, items):
        """移除多个元素"""
        removed = []
        for item in items:
            if item in self:
                self.remove(item)
                removed.append(item)
        if removed:
            self.history.append(('remove_many', removed, len(removed)))
