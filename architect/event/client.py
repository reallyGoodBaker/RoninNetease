from .core import EventChain, ChainedEvent
from ..component.core import _registerComponent, BaseCompClient

class EventReader(BaseCompClient):
    def onCreate(self, _):
        self.ev = None

    def event(self):
        # type: () -> ChainedEvent
        return self.ev
_registerComponent(False, EventReader, False, True)


class ClientEvents:
    globalEvents = {}

    @staticmethod
    def getOrCreateChain(eventType, isCustomEvent=False):
        # type: (str, bool) -> EventChain
        if eventType in ClientEvents.globalEvents:
            return ClientEvents.globalEvents[eventType]
        else:
            chain = EventChain()
            ClientEvents.globalEvents[eventType] = chain
            from ..subsystem import SubsystemManager
            SubsystemManager.getInstance().addListener(eventType, lambda ev: chain.dispatch(eventType, ev), isCustomEvent)
            return chain


def event(eventType, isCustomEvent=False):
    return ClientEvents.getOrCreateChain(eventType, isCustomEvent)