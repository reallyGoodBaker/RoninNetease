# Configuration API

`architect.conf` 模块定义了框架中使用的各种常量和配置项。这些配置项大部分用于内部标识，少量对外提供修改建议。

## 推荐修改的配置

#### `COMPONENT_NAMESPACE`

- **类型**: 字符串
- **说明**: 组件的命名空间，在注册组件时使用。建议修改为模组独有的值，避免冲突。
- **默认值**: `'xxx_roninComponent_xxx'`

#### `DB_NAME`

- **类型**: 字符串
- **说明**: 客户端本地数据库的命名空间。建议修改为模组独有的值。
- **默认值**: `'clientKVDb'`

#### `DB_GLOBAL_NAME`

- **类型**: 字符串
- **说明**: 全局数据库的命名空间。建议修改为模组独有的值。
- **默认值**: `'clientKVGlobal'`

#### `UI_NAMESPACE`

- **类型**: 字符串
- **说明**: UI 的命名空间，在注册 UI 时使用。建议修改为模组独有的值。
- **默认值**: `'xxx_roninUi_xxx'`

## 调度器调度名称 (不推荐修改)

这些常量定义了调度器任务的内部标识符，通常不建议修改。

#### `TIMER_TASK`

- **类型**: 字符串
- **说明**: 定时任务的标识符。
- **默认值**: `'TimerTask'`

#### `SCHED_BEFORE_UPDATE`

- **类型**: 字符串
- **说明**: 更新前调度阶段的标识符。
- **默认值**: `'BeforeUpdate'`

#### `SCHED_AFTER_UPDATE`

- **类型**: 字符串
- **说明**: 更新后调度阶段的标识符。
- **默认值**: `'AfterUpdate'`

#### `SCHED_UPDATE`

- **类型**: 字符串
- **说明**: 标准更新调度阶段的标识符。
- **默认值**: `'Update'`

#### `SCHED_EVENT`

- **类型**: 字符串
- **说明**: 事件触发时调度阶段的标识符。
- **默认值**: `'Event'`

#### `SCHED_AFTER_EVENT`

- **类型**: 字符串
- **说明**: 事件触发后调度阶段的标识符。
- **默认值**: `'AfterEvent'`

## 调度标志类

这些类提供对上述调度器调度名称的方便访问。

#### `SchedUpdateFlags` 类

定义了 `Tick` 或 `Render` 调度器的更新阶段标志。

- **`BeforeUpdate`**: 等同于 `SCHED_BEFORE_UPDATE`。
- **`AfterUpdate`**: 等同于 `SCHED_AFTER_UPDATE`。
- **`Update`**: 等同于 `SCHED_UPDATE`。

#### `SchedEventFlags` 类

定义了 `Event` 调度器的事件阶段标志。

- **`Event`**: 等同于 `SCHED_EVENT`。
- **`AfterEvent`**: 等同于 `SCHED_AFTER_EVENT`。
