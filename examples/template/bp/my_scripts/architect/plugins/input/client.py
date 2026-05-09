from ...core.loader import Plugin, PluginBase
from ...core.subsystem import SubsystemManager
from ...component import createSingletonComponent
from ...core.basic import localPlayerId
from ...event import CustomEvent

from .components.inputEx import InputExComponent
from .enum import IA_EVENT_PREFIX, InputState


@Plugin(
    'InputExPlugin',
    [1, 0, 1],
    'RGB39',
    'Extended input plugin'
)
class InputExPlugin(PluginBase):
    def onAttach(self, manager):
        # type: (SubsystemManager) -> None
        from .systems import inputExClient

    def onReady(self, manager):
        self._bindInputEx()

    def _bindInputEx(self):
        createSingletonComponent(InputExComponent)


def InputAction(actionName, inputState=InputState.Triggered):
    return CustomEvent(IA_EVENT_PREFIX + actionName + str(inputState))