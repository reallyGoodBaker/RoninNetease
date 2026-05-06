
# -*- coding: utf-8 -*-
from mod.common.mod import Mod
from .architect.conf import conf


@Mod.Binding(name = conf('MOD_NAME'), version = conf('MOD_VERSION'))
class ModBase(object):
    @Mod.InitServer()
    def initServer(self):
        from .architect.compact import createServer
        createServer()

    @Mod.InitClient()
    def initClient(self):
        from .architect.compact import createClient
        createClient()