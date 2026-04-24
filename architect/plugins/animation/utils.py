from ...core.unreliable import Unreliable
from .enum import AnimExEvents

class AnimationEventDispatcher(Unreliable):
    dispatchers = {}

    def __init__(self, animName):
        self.bindAnim = animName
        AnimationEventDispatcher.dispatchers[animName] = self

    def _callNamedMethod(self, methodName, *args):
        method = getattr(self, methodName, None)
        if callable(method):
            self.tryCall(method, *args)

    def dispatch(self, ev):
        entityId = ev['entityId']
        typeStr = ev['type']
        if typeStr == AnimExEvents.Interrupted:
            return self._callNamedMethod('onInterrupted', entityId)
        elif typeStr == AnimExEvents.Finish:
            return self._callNamedMethod('onFinish', entityId)
        elif typeStr == AnimExEvents.Notify:
            state = 'Start' if ev['state'] else 'End'
            notifyName = ev['notifyName']
            methodName = 'notify' + notifyName.capitalize() + state.capitalize()
            return self._callNamedMethod(methodName, entityId)


def AnimExListener(animName):
    def wrapper(cls):
        cls(animName)
        return cls
    return wrapper