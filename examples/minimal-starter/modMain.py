# -*- coding: utf-8 -*-

from mod.common.mod import Mod

# 换成实际的name和version
@Mod.Binding(name="modName", version="0.0.1")
class Invincible:
    @Mod.InitServer()
    def initServer(self):
        # 换成实际的导入路径
        from .architect.subsystem import SubsystemManager
        # 换成实际的命名空间和服务器名称
        SubsystemManager.createServer('namespace', 'server')
        from . import server

    @Mod.InitClient()
    def initClient(self):
        # 换成实际的导入路径
        from .architect.subsystem import SubsystemManager
        # 换成实际的命名空间和服务器名称
        SubsystemManager.createClient('namespace', 'client')
        from . import client