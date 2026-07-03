# -*- coding: utf-8 -*-
from ...core.loader import Plugin, PluginBase
from ...component import getOrCreateSingletonComponent


@Plugin(
    'CPlayerMotionPlugin',
    [1, 0, 0],
    'RGB39',
    '玩家运动组件（自动同步）'
)
class PlayerMotionPlugin(PluginBase):
    def onReady(self, manager):
        from .playerMotionComp import PlayerMotionComponent
        getOrCreateSingletonComponent(PlayerMotionComponent)
