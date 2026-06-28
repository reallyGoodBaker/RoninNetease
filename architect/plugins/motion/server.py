from ...core.loader import Plugin, PluginBase
from ...component import getOrCreateSingletonComponent


@Plugin(
    'SPlayerMotionPlugin',
    [1, 0, 0],
    'RGB39',
    '玩家运动组件（自动同步）'
)
class PlayerMotionPlugin(PluginBase):
    def onCreate(self):
        from .system.sync import PlayerMotionSyncServer