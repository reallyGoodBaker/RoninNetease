from .core import EventChain, ChainedEvent
from ..component.core import _registerComponent, BaseCompServer


class EventReader(BaseCompServer):
    def onCreate(self, _):
        self.ev = None

    def event(self):
        # type: () -> ChainedEvent
        return self.ev
_registerComponent(True, EventReader, False, True)


class ServerEvents:
    globalEvents = {}

    @staticmethod
    def getOrCreateChain(eventType, isCustomEvent=False):
        # type: (str, bool) -> EventChain
        if eventType in ServerEvents.globalEvents:
            return ServerEvents.globalEvents[eventType]
        else:
            chain = EventChain()
            ServerEvents.globalEvents[eventType] = chain
            from ..subsystem import SubsystemManager
            SubsystemManager.getInstance().addListener(eventType, lambda ev: chain.dispatch(eventType, ev), isCustomEvent)
            return chain


def event(eventType, isCustomEvent=False):
    return ServerEvents.getOrCreateChain(eventType, isCustomEvent)