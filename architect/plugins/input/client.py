from ...core.loader import Plugin, PluginBase
from ...core.subsystem import SubsystemManager
from ...component import Component, BaseCompClient, createSingletonComponent
from ...core.basic import localPlayer


@Component(singleton=True)
class InputExComponent(BaseCompClient):
    def onCreate(self, entityId):
        self.pressingKeys = set()
        self.inputStack = []


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
        )

    def _bindInputEx(self, player):
        if localPlayer() == player:
            createSingletonComponent(InputExComponent)