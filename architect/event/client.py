from .core import EventChain
from ..component import Component, BaseCompClient


@Component(singleton=True)
class EventReader(BaseCompClient):
    def onCreate(self, _):
        self.ev = None


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