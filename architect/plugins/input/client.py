from ...core.loader import Plugin, PluginBase
from ...core.subsystem import SubsystemManager
from ...component import createSingletonComponent
from ...core.basic import localPlayerId

from .components.inputEx import InputExComponent


@Plugin(
    'InputExPlugin',
    [1, 0, 1],
    'RGB39',
    'Extended input plugin'
)
class InputExPlugin(PluginBase):
    def onAttach(self, manager):
        # type: (SubsystemManager) -> None
        manager.addListener(
            'AddPlayerCreatedClientEvent',
            self._bindInputEx
        )

    def _bindInputEx(self, ev):
        if localPlayerId() == ev.playerId:
            createSingletonComponent(InputExComponent)