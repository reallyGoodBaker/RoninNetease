# 状态树 (State Tree) 模块 (`__init__.py`)

`architect.fsm.stateTree.__init__.py` 是状态树系统的入口模块。

## 说明

该文件当前为空，可能用于未来扩展或作为包导入的占位符。

## 相关子模块

状态树系统包含以下子模块：

1. **`client.py`** - 客户端状态树实现。
2. **`common.py`** - 通用状态树组件和基础类。
3. **`server.py`** - 服务端状态树实现。

## 使用建议

由于该文件为空，建议直接导入具体的子模块：

```python
# 导入通用状态树组件
from ..architect.fsm.stateTree.common import StateTree, StateNode

# 导入客户端状态树
from ..architect.fsm.stateTree.client import ClientStateTree

# 导入服务端状态树
from ..architect.fsm.stateTree.server import ServerStateTree
```

## 状态树概念

状态树是一种层次化的状态机，允许状态嵌套和并行执行。与传统的有限状态机 (FSM) 相比，状态树提供了更灵活的状态管理能力。

### 主要特点

1. **层次结构**: 状态可以包含子状态，形成树状结构。
2. **并行执行**: 多个状态可以同时激活。
3. **状态转换**: 支持复杂的转换逻辑。
4. **事件处理**: 状态可以响应事件并触发转换。

## 注意事项

- 该文件可能在未来版本中添加导出内容。
- 请参考具体子模块的文档了解详细用法。
- 状态树系统是 `deprecated.py` 中经典 FSM 的现代替代方案。
