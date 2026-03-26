# 推荐修改的配置
COMPONENT_NAMESPACE = 'xxx_roninComponent_xxx'  # 组件命名空间
DB_NAME = 'clientKVDb'                          # 数据库命名空间
DB_GLOBAL_NAME = 'clientKVGlobal'               # 全局数据库命名空间
UI_NAMESPACE = 'xxx_roninUi_xxx'                # UI命名空间

# 改了也没什么意义的配置
ANNOTATION = '_annotation'                      # 装饰器标记
COMPONENT_TAG = '_component'                    # 组件标记
EVENT_LISTENER = '_event_listener'              # 事件监听器标记
CUSTOM_EVENT = '_custom_event'                  # 自定义事件标记
SYSTEM_SCHED_ANNO = '_system_sched'             # 系统调度器标记

# 调度器调度名称（不推荐修改）
TIMER_TASK = 'TimerTask'                        # 定时任务
SCHED_BEFORE_UPDATE = 'BeforeUpdate'            # 更新前调度
SCHED_AFTER_UPDATE = 'AfterUpdate'              # 更新后调度
SCHED_UPDATE = 'Update'                         # 更新调度