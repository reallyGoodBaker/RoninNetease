# 有限状态机 (FSM) 模块 (`__init__.py`)

`architect.fsm.__init__.py` 是有限状态机 (Finite State Machine) 系统的入口模块。

## 说明

该文件当前为空，可能用于未来扩展或作为包导入的占位符。

## 相关子模块

有限状态机系统包含以下子模块：

1. **`deprecated.py`** - 已弃用的 FSM 实现。
2. **`stateTree/`** - 状态树实现，包含：
   - `__init__.py` - 状态树入口模块。
   - `client.py` - 客户端状态树。
   - `common.py` - 通用状态树组件。
   - `server.py` - 服务端状态树。

## 使用建议

由于该文件为空，建议直接导入具体的子模块：

```python
# 导入状态树模块
from ..architect.fsm.stateTree import StateTree, StateNode

# 导入已弃用的 FSM 模块（如果需要）
from ..architect.fsm.deprecated import OldFSM
```

## 注意事项

- 该文件可能在未来版本中添加导出内容。
- 请参考具体子模块的文档了解详细用法。
