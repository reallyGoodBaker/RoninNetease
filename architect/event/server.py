from .core import EventChain, EventListener, CustomEvent


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
            SubsystemManager.getInst().addListener(eventType, lambda ev: chain.dispatch(eventType, ev), isCustomEvent)
            return chain

def event(eventType, isCustomEvent=False):
    return ServerEvents.getOrCreateChain(eventType, isCustomEvent)