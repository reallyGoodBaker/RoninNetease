# 推荐修改的配置
COMPONENT_NAMESPACE = 'xxx_roninComponent_xxx'  # 组件命名空间
DB_NAME = 'clientKVDb'                          # 数据库命名空间
DB_GLOBAL_NAME = 'clientKVGlobal'               # 全局数据库命名空间
UI_NAMESPACE = 'xxx_roninUi_xxx'                # UI命名空间

# 改了也没什么意义的配置
ANNOTATION = '_annotation'                      # 装饰器标记
COMPONENT_TAG = '_component'                    # 组件标记
PERSIST_INFO = '_persist_keys'                  # 持久化键标记
EVENT_LISTENER = '_event_listener'              # 事件监听器标记
CUSTOM_EVENT = '_custom_event'                  # 自定义事件标记
SYSTEM_SCHED_ANNO = '_system_sched'             # 系统调度器标记
UI_DEF = '_ui_def'                              # UI定义标记
UI_SINK = '_ui_binder'                          # UI绑定标记
UI_SCREEN = '_ui_screen'                        # UI屏幕标记
UI_HUD = '_ui_hud'                              # UI HUD标记
UI_GESTURE = '_ui_gesture'                      # UI手势类型标记

# 调度器调度名称（不推荐修改）
TIMER_TASK = 'TimerTask'                        # 定时任务
SCHED_BEFORE_UPDATE = 'BeforeUpdate'            # 更新前调度
SCHED_AFTER_UPDATE = 'AfterUpdate'              # 更新后调度
SCHED_UPDATE = 'Update'                         # 更新调度
SCHED_EVENT = 'Event'                           # 事件时调度
SCHED_AFTER_EVENT = 'AfterEvent'                # 事件后调度

class SchedUpdateFlags:
    BeforeUpdate = SCHED_BEFORE_UPDATE
    AfterUpdate = SCHED_AFTER_UPDATE
    Update = SCHED_UPDATE

class SchedEventFlags:
    Event = SCHED_EVENT
    AfterEvent = SCHED_AFTER_EVENT