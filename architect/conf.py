# coding=utf-8
"""
引擎约束说明 (Engine Constraint Notes)

本文件与 core/configurator.py 构成双轨制配置体系，这是网易引擎 ImportModule
限制下的必要分层：

- 网易引擎不支持原生 __import__ 动态导入，其 ImportModule API 必须在引擎加载
  完毕后才能调用。
- 因此框架早期初始化（Loader 注册、子系统扫描路径等）只能通过本文件获取配置，
  使用 `try: from ... import conf` 在引擎加载前即可读取。
- 运行时热重载、类型安全 setter 等高级功能则由 configurator.py 提供，它需要
  引擎 ImportModule 就绪后才能工作。

将两套系统合并为单一入口在现行引擎约束下不可行。请勿移除任一配置体系。

这里是引擎配置, 不建议直接修改.
MOD_* 和 PLUGINS 遵循覆盖原则, 用户可以在脚本根目录下创建 conf.py 覆盖默认配置.
如果你不知道有哪些配置可以修改, 请将引擎配置中 “推荐修改的配置” 和 “插件列表” 复制到你的 conf.py 中
"""
class _ModuleLocator: pass
__modname__ = _ModuleLocator.__module__[:_ModuleLocator.__module__.find('.')]



# 推荐修改的配置
MOD_NAME = __modname__
MOD_VERSION = '1.0.0'
MOD_ENGINE_NAME = MOD_NAME
MOD_SYSTEM_NAME = 'ModSubsystem'
MOD_SERVER_MODULES = []
MOD_CLIENT_MODULES = []

# 插件列表
"""
$vendor为系统插件, $user为用户插件
系统插件在{modname}/architect/plugins目录下
用户插件在{modname}/plugins目录下
"""
PLUGINS = [
    '$vendor.event',        # 事件系统
    '$vendor.motion',       # 运动系统
]







# 改了也没什么意义的配置
COMPONENT_NAMESPACE = 'xxx_roninComponent_xxx'  # 组件命名空间
DB_NAME = 'clientKVDb'                          # 数据库命名空间
DB_GLOBAL_NAME = 'clientKVGlobal'               # 全局数据库命名空间
UI_NAMESPACE = 'xxx_roninUi_xxx'                # UI命名空间
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

INTERNAL_METHOD = '_internal_method'
ASPECT = '_Aspect'

class Aspects:
    Before = '_asp_before'
    After = '_asp_after'
    AfterReturning = '_asp_afterReturning'
    AfterThrowing = '_asp_afterThrowing'
    Replace = '_asp_replace'


try:
    from ... import conf as userConf
except:
    userConf = object()
vendorConf = globals()

def conf(key):
    try:
        return userConf.__dict__[key]
    except:
        return vendorConf[key]