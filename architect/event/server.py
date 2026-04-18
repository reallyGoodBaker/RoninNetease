from .core import EventChain


class ServerEvents:
    globalEvents = {}

    @staticmethod
    def getOrCreateChain(eventType, isCustomEvent=False):
        # type: (str, bool) -> EventChain
        if (eventType, isCustomEvent) in ServerEvents.globalEvents:
            return ServerEvents.globalEvents[(eventType, isCustomEvent)]
        else:
            chain = EventChain()
            ServerEvents.globalEvents[(eventType, isCustomEvent)] = chain
            from ..core.subsystem import SubsystemManager
            SubsystemManager.getInstance().addListener(eventType, lambda ev: chain.dispatch(eventType, ev), isCustomEvent)
            return chain


def event(eventType, isCustomEvent=False):
    return ServerEvents.getOrCreateChain(eventType, isCustomEvent)