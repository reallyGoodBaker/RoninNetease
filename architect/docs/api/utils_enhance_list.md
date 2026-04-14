# 增强列表工具 (EnhanceList) API

`architect.utils.enhance.list` 模块提供了增强的列表操作功能，包括安全移除、分块、展平、压缩和填充等操作。

## 函数

### `remove(list, item)`

安全地从列表中移除元素。

- **`list`**: 要操作的列表
- **`item`**: 要移除的元素
- **返回值**: 布尔值，True表示成功移除，False表示元素不存在
- **类型提示**: `(list, object) -> bool`

### `chunk(list, size)`

将列表分块。

- **`list`**: 要分块的列表
- **`size`**: 每块的大小
- **返回值**: 分块后的列表（列表的列表）
- **类型提示**: `(list, int) -> list`

### `flatten(list)`

展平嵌套列表。

- **`list`**: 要展平的嵌套列表
- **返回值**: 展平后的列表
- **类型提示**: `(list) -> list`

### `compact(list)`

压缩列表，移除所有假值（False, None, 0, '', []等）。

- **`list`**: 要压缩的列表
- **返回值**: 压缩后的列表
- **类型提示**: `(list) -> list`

### `fill(list, item, start=0, end=None)`

用指定元素填充列表的指定范围。

- **`list`**: 要填充的列表
- **`item`**: 填充元素
- **`start`**: 起始索引（默认0）
- **`end`**: 结束索引（默认列表长度）
- **返回值**: 填充后的列表
- **类型提示**: `(list, object, int, int) -> list`

### `without(list, item)`

创建不包含指定元素的新列表。

- **`list`**: 原始列表
- **`item`**: 要排除的元素
- **返回值**: 不包含指定元素的新列表
- **类型提示**: `(list, object) -> list`

## 使用示例

### 1. 基本列表操作

```python
from ..architect.utils.enhance.list import (
    remove, chunk, flatten, compact, fill, without
)

class ListOperations:
    def __init__(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    def demonstrate_remove(self):
        """演示安全移除"""
        print("原始列表:", self.data)
        
        # 安全移除存在的元素
        result = remove(self.data, 3)
        print(f"移除元素3: {result}, 列表: {self.data}")
        
        # 安全移除不存在的元素
        result = remove(self.data, 99)
        print(f"移除元素99: {result}, 列表: {self.data}")
        
        return self.data
    
    def demonstrate_chunk(self):
        """演示分块"""
        print("原始列表:", self.data)
        
        # 分块大小为3
        chunks = chunk(self.data, 3)
        print(f"分块(大小3): {chunks}")
        
        # 分块大小为4
        chunks = chunk(self.data, 4)
        print(f"分块(大小4): {chunks}")
        
        return chunks
    
    def demonstrate_flatten(self):
        """演示展平"""
        nested_list = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
        print("嵌套列表:", nested_list)
        
        flattened = flatten(nested_list)
        print(f"展平后: {flattened}")
        
        return flattened
    
    def demonstrate_compact(self):
        """演示压缩"""
        mixed_list = [1, 0, 2, None, 3, '', 4, [], 5, False, 6]
        print("混合列表:", mixed_list)
        
        compacted = compact(mixed_list)
        print(f"压缩后: {compacted}")
        
        return compacted
    
    def demonstrate_fill(self):
        """演示填充"""
        test_list = [1, 2, 3, 4, 5]
        print("原始列表:", test_list)
        
        # 填充索引1到3
        filled = fill(test_list.copy(), 0, 1, 3)
        print(f"填充[1:3]为0: {filled}")
        
        # 填充整个列表
        filled = fill(test_list.copy(), 'X')
        print(f"填充整个列表为'X': {filled}")
        
        # 填充最后两个元素
        filled = fill(test_list.copy(), 9, -2)
        print(f"填充最后两个元素为9: {filled}")
        
        return filled
    
    def demonstrate_without(self):
        """演示排除"""
        test_list = [1, 2, 3, 2, 4, 2, 5]
        print("原始列表:", test_list)
        
        # 排除所有2
        filtered = without(test_list, 2)
        print(f"排除所有2: {filtered}")
        
        # 排除不存在的元素
        filtered = without(test_list, 99)
        print(f"排除99: {filtered}")
        
        return filtered
    
    def run_all_demos(self):
        """运行所有演示"""
        print("=== 增强列表工具演示 ===")
        
        print("\n1. 安全移除演示:")
        self.demonstrate_remove()
        
        print("\n2. 分块演示:")
        self.demonstrate_chunk()
        
        print("\n3. 展平演示:")
        self.demonstrate_flatten()
        
        print("\n4. 压缩演示:")
        self.demonstrate_compact()
        
        print("\n5. 填充演示:")
        self.demonstrate_fill()
        
        print("\n6. 排除演示:")
        self.demonstrate_without()
```

### 2. 实际应用场景

```python
from ..architect.utils.enhance.list import (
    remove, chunk, flatten, compact, fill, without
)

class ListUtilities:
    @staticmethod
    def safe_remove_items(items_list, items_to_remove):
        """安全移除多个元素"""
        results = []
        for item in items_to_remove:
            success = remove(items_list, item)
            results.append((item, success))
        
        removed_count = sum(1 for _, success in results if success)
        print(f"成功移除了 {removed_count}/{len(items_to_remove)} 个元素")
        return results
    
    @staticmethod
    def batch_process(items, batch_size, process_func):
        """批量处理列表项"""
        batches = chunk(items, batch_size)
        results = []
        
        for i, batch in enumerate(batches):
            print(f"处理批次 {i+1}/{len(batches)} (大小: {len(batch)})")
            result = process_func(batch)
            results.append(result)
        
        return results
    
    @staticmethod
    def flatten_nested_data(nested_data):
        """展平嵌套数据结构"""
        # 递归展平
        def recursive_flatten(data):
            if isinstance(data, list):
                flattened = []
                for item in data:
                    if isinstance(item, list):
                        flattened.extend(recursive_flatten(item))
                    else:
                        flattened.append(item)
                return flattened
            else:
                return [data]
        
        return recursive_flatten(nested_data)
    
    @staticmethod
    def clean_data(data_list):
        """清理数据列表"""
        # 压缩假值
        cleaned = compact(data_list)
        
        # 移除特定的无效值
        cleaned = without(cleaned, 'N/A')
        cleaned = without(cleaned, 'null')
        cleaned = without(cleaned, 'undefined')
        
        print(f"清理前: {len(data_list)} 个元素")
        print(f"清理后: {len(cleaned)} 个元素")
        
        return cleaned
    
    @staticmethod
    def create_template(size, template_value):
        """创建模板列表"""
        template = []
        fill(template, template_value, 0, size)
        return template
    
    @staticmethod
    def paginate_items(items, page_size, page_num):
        """分页显示列表项"""
        # 分块
        pages = chunk(items, page_size)
        
        # 检查页码是否有效
        if page_num < 1 or page_num > len(pages):
            print(f"无效页码: {page_num} (总页数: {len(pages)})")
            return []
        
        current_page = pages[page_num - 1]
        print(f"第 {page_num}/{len(pages)} 页, 显示 {len(current_page)} 个项目")
        
        return current_page
    
    @staticmethod
    def filter_by_condition(items, condition):
        """按条件过滤列表"""
        # 使用without的变体
        filtered = []
        for item in items:
            if condition(item):
                filtered.append(item)
        
        return filtered
    
    @staticmethod
    def replace_items(items, old_value, new_value):
        """替换列表中的元素"""
        # 先移除旧值，再添加新值
        result = items.copy()
        
        # 移除所有旧值
        while remove(result, old_value):
            pass
        
        # 添加新值（保持相同数量）
        for _ in range(items.count(old_value)):
            result.append(new_value)
        
        return result
    
    @staticmethod
    def analyze_list(items):
        """分析列表"""
        analysis = {
            'total_count': len(items),
            'unique_count': len(set(items)),
            'has_duplicates': len(items) != len(set(items)),
            'empty': len(items) == 0,
            'nested': any(isinstance(item, list) for item in items),
            'compacted_count': len(compact(items)),
            'chunks_3': len(chunk(items, 3)) if items else 0
        }
        
        return analysis
```

### 3. 游戏数据管理

```python
from ..architect.utils.enhance.list import (
    remove, chunk, flatten, compact, fill, without
)

class GameDataManager:
    def __init__(self):
        self.player_inventory = []
        self.game_items = []
        self.quest_log = []
    
    def manage_inventory(self):
        """管理玩家库存"""
        print("=== 玩家库存管理 ===")
        
        # 示例库存
        self.player_inventory = [
            'sword', 'shield', 'potion', 'potion', 'key',
            '', None, 0, 'armor', 'potion', False, 'gold'
        ]
        
        print(f"原始库存: {self.player_inventory}")
        print(f"库存大小: {len(self.player_inventory)}")
        
        # 清理库存（移除假值）
        self.player_inventory = compact(self.player_inventory)
        print(f"清理后库存: {self.player_inventory}")
        print(f"清理后大小: {len(self.player_inventory)}")
        
        # 移除特定物品
        removed = remove(self.player_inventory, 'key')
        print(f"移除钥匙: {removed}")
        
        # 统计药水数量
        potion_count = self.player_inventory.count('potion')
        print(f"药水数量: {potion_count}")
        
        # 排除所有药水（查看但不移除）
        without_potions = without(self.player_inventory, 'potion')
        print(f"不含药水的库存: {without_potions}")
        
        return self.player_inventory
    
    def organize_items(self, items):
        """组织游戏物品"""
        print("=== 游戏物品组织 ===")
        
        # 分块显示（每行5个）
        chunks = chunk(items, 5)
        
        print("物品分块显示:")
        for i, chunk_items in enumerate(chunks):
            print(f"  块 {i+1}: {chunk_items}")
        
        # 填充空位
        if len(items) < 20:
            fill(items, 'empty', len(items), 20)
            print(f"填充空位后: {items}")
        
        return items
    
    def manage_quests(self):
        """管理任务日志"""
        print("=== 任务日志管理 ===")
        
        # 嵌套任务结构
        self.quest_log = [
            ['main_quest_1', 'main_quest_2'],
            ['side_quest_1', 'side_quest_2', 'side_quest_3'],
            ['completed_quests'],
            ['failed_quests']
        ]
        
        print(f"嵌套任务结构: {self.quest_log}")
        
        # 展平任务列表
        flat_quests = flatten(self.quest_log)
        print(f"展平任务列表: {flat_quests}")
        
        # 按类型分组（示例）
        main_quests = [q for q in flat_quests if 'main' in q]
        side_quests = [q for q in flat_quests if 'side' in q]
        
        print(f"主线任务: {main_quests}")
        print(f"支线任务: {side_quests}")
        
        return {
            'flat': flat_quests,
            'main': main_quests,
            'side': side_quests
        }
    
    def process_game_data(self, raw_data):
        """处理游戏数据"""
        print("=== 游戏数据处理 ===")
        
        # 清理数据
        cleaned_data = compact(raw_data)
        print(f"清理后数据: {cleaned_data}")
        
        # 移除无效条目
        invalid_entries = ['invalid', 'error', 'corrupted']
        for invalid in invalid_entries:
            cleaned_data = without(cleaned_data, invalid)
        
        print(f"移除无效条目后: {cleaned_data}")
        
        # 分块处理
        if cleaned_data:
            data_chunks = chunk(cleaned_data, 10)
            print(f"数据分块数: {len(data_chunks)}")
            
            # 处理每个块
            processed_chunks = []
            for i, chunk_data in enumerate(data_chunks):
                # 这里可以添加实际的处理逻辑
                processed = f"块{i+1}_已处理"
                processed_chunks.append(processed)
            
            return processed_chunks
        
        return []
    
    def create_item_grid(self, rows, cols, default_item='empty'):
        """创建物品网格"""
        print(f"=== 创建物品网格 ({rows}x{cols}) ===")
        
        # 创建空网格
        grid = []
        for _ in range(rows):
            row = []
            fill(row, default_item, 0, cols)
            grid.append(row)
        
        print("物品网格:")
        for i, row in enumerate(grid):
            print(f"  行 {i+1}: {row}")
        
        return grid
    
    def update_inventory_slots(self, inventory, slots_to_update):
        """更新库存槽位"""
        print("=== 更新库存槽位 ===")
        
        # 确保库存足够大
        max_slot = max(slot for slot, _ in slots_to_update) if slots_to_update else 0
        if len(inventory) <= max_slot:
            fill(inventory, 'empty', len(inventory), max_slot + 1)
        
        # 更新槽位
        for slot, item in slots_to_update:
            if 0 <= slot < len(inventory):
                inventory[slot] = item
                print(f"  槽位 {slot}: 设置为 {item}")
        
        print(f"更新后库存: {inventory}")
        return inventory
```

### 4. 性能优化工具

```python
from ..architect.utils.enhance.list import (
    remove, chunk, flatten, compact, fill, without
)
import time

class PerformanceOptimizer:
    @staticmethod
    def benchmark_list_operations():
        """基准测试列表操作"""
        print("=== 列表操作性能测试 ===")
        
        # 创建测试数据
        test_size = 10000
        test_list = list(range(test_size))
        
        # 测试remove
        start_time = time.time()
        for i in range(100):
            test_copy = test_list.copy()
            remove(test_copy, i)
        remove_time = time.time() - start_time
        
        # 测试chunk
        start_time = time.time()
        for _ in range(100):
            chunk(test_list, 100)
        chunk_time = time.time() - start_time
        
        # 测试flatten
        nested_list = [test_list[:100] for _ in range(100)]
        start_time = time.time()
        for _ in range(100):
            flatten(nested_list)
        flatten_time = time.time() - start_time
        
        # 测试compact
        mixed_list = test_list + [None, 0, '', False] * 100
        start_time = time.time()
        for _ in range(100):
            compact(mixed_list)
        compact_time = time.time() - start_time
        
        # 测试fill
        start_time = time.time()
        for _ in range(100):
            test_copy = test_list.copy()
            fill(test_copy, 0, 0, 100)
        fill_time = time.time() - start_time
        
        # 测试without
        start_time = time.time()
        for i in range(100):
            without(test_list, i)
        without_time = time.time() - start_time
        
        print(f"测试数据大小: {test_size}")
        print(f"remove 操作时间: {remove_time:.4f}秒")
        print(f"chunk 操作时间: {chunk_time:.4f}秒")
        print(f"flatten 操作时间: {flatten_time:.4f}秒")
        print(f"compact 操作时间: {compact_time:.4f}秒")
        print(f"fill 操作时间: {fill_time:.4f}秒")
        print(f"without 操作时间: {without_time:.4f}秒")
        
        return {
            'remove': remove_time,
            'chunk': chunk_time,
            'flatten': flatten_time,
            'compact': compact_time,
            'fill': fill_time,
            'without': without_time
        }
    
    @staticmethod
    def optimize_memory_usage(data_lists):
        """优化内存使用"""
        print("===