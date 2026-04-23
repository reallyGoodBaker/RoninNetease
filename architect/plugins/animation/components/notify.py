from ....core.annotation import AnnotationHelper


AnimNotifyRegistry = {}


def NotifyTrack(animName):
    def decorator(cls):
        AnimNotifyRegistry[animName] = cls
        return cls
    return decorator


def Notify(time):
    def decorator(func):
        AnnotationHelper.addAnnotation(func, 'notify_' + func.__name__, time)
        return func
    return decorator


class AnimationNotifyTrack(object):
    def __init__(self):
        self.