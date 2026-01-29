# RoninNetease
ECS Framework for minecraft netease



# QuickStart

复制 `architect` 中的代码到你的项目

```py
from mod.common.mod import Mod

@Mod.Binding(name="mod", version="0.0.1")
class Invincible:
    @Mod.InitServer()
    def initServer(self):
        # 写在这里是因为如果直接 import 会导致 SubsystemManager 在客户端和服务端同时加载两次
        from ...architect.subsystem import SubsystemManager
        SubsystemManager.createServer('namespace', 'server')

    @Mod.InitClient()
    def initClient(self):
        # 同上
        from ...architect.subsystem import SubsystemManager
        SubsystemManager.createClient('namespace', 'client')
```

这样就已经运行起来了，如果需要添加 `Subsystem` 请参考 `examples/minimal-starter`

**这里推荐直接复制 minimal-starter 并修改进行使用！！！！**



#### 从 `minimal-starter` 开始

将`minimal-starter`直接复制到你的行为包下并将architect放到其中 (`minimal-starter`目录中应该包含architect包)

直接修改 `test.py` 中的代码即可

**需要注意的是，`minimal-starter/client/__init__.py` 是有内容的, 服务端同理, 只有导入了才能让装饰器运行！！**



#### 事件监听

`event` 包提供了基础的事件监听器，并实现了对原生事件的监听，只需要在Subsystem内使用对应端的EventListener装饰器即可实现简单监听：

```py
from ..architect.event.client import EventListener
from ..architect.event.core import ChainedEvent

@SubsystemClient
class TestSubsystem(ClientSubsystem):

    # 监听 OnLocalPlayerStopLoading 事件
    @EventListener('OnLocalPlayerStopLoading')
    def onLocalPlayerStopLoading(self, event):
        # type: (ChainedEvent) -> None
        print "Local player stopped loading!
```

需要注意的是，通过 `EventListener` 或者 `Subsystem.on`/`Subsystem.listen` 注册的监听器使用了一套不同于原版的事件处理机制，传回的 `event` 对象类型不是 `dict`, 而是 `ChainedEvent`，关于 `ChainedEvent` 类的信息可以直接查看源码

如果你需要原版的 `dict` 类型的event，你也可以使用 `ChainedEvent.dict()` 直接获取