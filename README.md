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