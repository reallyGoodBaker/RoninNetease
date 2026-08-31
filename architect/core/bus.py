# coding=utf-8


class CommandBus:
    """
    本地同步命令总线，解耦子系统间通信。

    子系统通过此总线声明和调用命令，而非直接引用其他子系统实例，
    从而支持 mock、限流、日志等横切关注点。

    使用方式:
        manager = SubsystemManager.getInstance()

        # 注册命令处理器，返回注销函数
        unregister = manager.bus.register('spawn_npc', handler)

        # 同步执行命令，收集所有处理器返回值
        results = manager.bus.execute('spawn_npc', template, location)

        # 注销命令
        unregister()
    """
    def __init__(self):
        self._handlers = {}  # type: dict[str, list]

    def register(self, commandName, handler):
        # type: (str, callable) -> callable
        """
        注册命令处理器，返回一个注销函数。

        :param commandName: 命令名称（字符串）
        :param handler:      处理器可调用对象
        :return:            无参注销函数
        """
        self._handlers.setdefault(commandName, []).append(handler)
        def unregister():
            handlers = self._handlers.get(commandName)
            if handlers and handler in handlers:
                handlers.remove(handler)
        return unregister

    def execute(self, commandName, *args, **kwargs):
        # type: (str, *object, **object) -> list
        """
        同步执行命名命令，调用所有已注册的处理器，
        并按注册顺序收集返回值列表。

        :param commandName: 命令名称
        :return:             处理器返回值列表
        """
        results = []
        for handler in self._handlers.get(commandName, []):
            results.append(handler(*args, **kwargs))
        return results

    def hasCommand(self, commandName):
        # type: (str) -> bool
        """检查是否有处理器注册了给定命令"""
        return bool(self._handlers.get(commandName))

    def clearCommand(self, commandName):
        # type: (str) -> None
        """移除给定命令的所有处理器"""
        self._handlers.pop(commandName, None)

    def clearAll(self):
        # type: () -> None
        """移除所有已注册的命令"""
        self._handlers.clear()