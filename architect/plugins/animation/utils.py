from ...core.unreliable import Unreliable
from .enum import AnimExEvents

class AnimationEventDispatcher(Unreliable):
    dispatchers = {}
    animDispatcherMapping = {}

    @classmethod
    def getOrCreate(cls, animName):
        dispatcher = AnimationEventDispatcher.dispatchers.get(cls.__name__)
        if dispatcher is None:
            dispatcher = cls()
            AnimationEventDispatcher.dispatchers[cls.__name__] = dispatcher
        AnimationEventDispatcher.animDispatcherMapping[animName] = dispatcher
        return dispatcher

    def _callNamedMethod(self, methodName, *args):
        method = getattr(self, methodName, None)
        if callable(method):
            self.tryCall(method, *args)

    def dispatch(self, ev, animComp):
        entityId = ev['entityId']
        typeStr = ev['type']
        if typeStr == AnimExEvents.Interrupted:
            return self._callNamedMethod('onInterrupted', entityId, animComp)
        elif typeStr == AnimExEvents.Finish:
            return self._callNamedMethod('onFinish', entityId, animComp)
        elif typeStr == AnimExEvents.Notify:
            state = 'Start' if ev['state'] else 'End'
            notifyName = ev['notifyName']
            methodName = 'notify' + notifyName.capitalize() + state.capitalize()
            return self._callNamedMethod(methodName, entityId, animComp)


def AnimExListener(animName):
    def wrapper(cls):
        AnimationEventDispatcher.getOrCreate(animName)
        return cls
    return wrapper