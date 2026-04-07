from .core import EventChain
from ..component import Component, BaseCompServer


@Component(singleton=True)
class EventReader(BaseCompServer):
    def onCreate(self, _):
        self.ev = None


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