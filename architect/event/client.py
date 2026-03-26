from .core import EventChain
from ..annotation import AnnotationHelper
from ..conf import EVENT_LISTENER, CUSTOM_EVENT


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
            SubsystemManager.getInst().addListener(eventType, lambda ev: chain.dispatch(eventType, ev), isCustomEvent)
            return chain

def event(eventType, isCustomEvent=False):
    return ClientEvents.getOrCreateChain(eventType, isCustomEvent)

def EventListener(eventType, isCustomEvent=False):
    def decorator(fn):
        # 标记方法为事件监听器
        AnnotationHelper.addAnnotation(fn, EVENT_LISTENER, eventType)
        if isCustomEvent:
            AnnotationHelper.addAnnotation(fn, CUSTOM_EVENT, True)
        return fn
    return decorator