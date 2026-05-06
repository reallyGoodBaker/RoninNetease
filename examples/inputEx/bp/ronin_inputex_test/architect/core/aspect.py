from .annotation import AnnotationHelper
from ..conf import Aspects, ASPECT


def Before(methodName):
    # type: (str) -> AnnotationHelper
    """
    :example:
    ```
    @Before("onTick")
    def onTickBefore(self, targetInst, args, kwargs):
        pass
    ```
    """
    def wrapper(func):
        AnnotationHelper.addAnnotation(func, ASPECT, (Aspects.Before, methodName))
        return func

    return wrapper


def After(methodName):
    # type: (str) -> AnnotationHelper
    """
    :example:
    ```
    @After("onTick")
    def onTickAfter(self, targetInst, args, kwargs):
        pass
    ```
    """    
    def wrapper(func):
        AnnotationHelper.addAnnotation(func, ASPECT, (Aspects.After, methodName))
        return func

    return wrapper


def AfterReturning(methodName):
    # type: (str) -> AnnotationHelper
    """
    :example:
    ```
    @AfterReturning("onTick")
    def onTickAfterReturning(self, targetInst, returnVal, args, kwargs):
        pass
    ```
    """
    def wrapper(func):
        AnnotationHelper.addAnnotation(func, ASPECT, (Aspects.AfterReturning, methodName))
        return func

    return wrapper


def AfterThrowing(methodName):
    # type: (str) -> AnnotationHelper
    """
    :example:
    ```
    @AfterThrowing("onTick")
    def onTickAfterThrowing(self, targetInst, e, args, kwargs):
        pass
    ```
    """
    def wrapper(func):
        AnnotationHelper.addAnnotation(func, ASPECT, (Aspects.AfterThrowing, methodName))
        return func

    return wrapper


def Replace(methodName):
    # type: (str) -> AnnotationHelper
    """
    :example:
    ```
    @Replace("onTick")
    def onTickReplace(self, targetInst, targetMethod, *args, **kwargs):
        pass
    ```
    """
    def wrapper(func):
        AnnotationHelper.addAnnotation(func, ASPECT, (Aspects.Replace, methodName))
        return func

    return wrapper


class AspectUtils(object):
    _aspectInst = {}


    @staticmethod
    def before(targetCls, methodName, wrapper):
        if not hasattr(targetCls, methodName):
            return
        target = getattr(targetCls, methodName)
        aspect = AspectUtils._aspectInst.get(targetCls, None)
        def _before(inst, *args, **kwargs):
            wrapper(aspect, inst, args, kwargs)
            return target(inst, args, kwargs)
        setattr(targetCls, methodName, _before)


    @staticmethod
    def after(targetCls, methodName, wrapper):
        if not hasattr(targetCls, methodName):
            return
        target = getattr(targetCls, methodName)
        aspect = AspectUtils._aspectInst.get(targetCls, None)
        def _after(inst, *args, **kwargs):
            result = target(inst, args, kwargs)
            wrapper(aspect, inst, args, kwargs)
            return result
        setattr(targetCls, methodName, _after)


    @staticmethod
    def afterReturning(targetCls, methodName, wrapper):
        if not hasattr(targetCls, methodName):
            return
        target = getattr(targetCls, methodName)
        aspect = AspectUtils._aspectInst.get(targetCls, None)
        def _afterReturning(inst, args, kwargs):
            result = target(inst, args, kwargs)
            wrapper(aspect, inst, result, *args, **kwargs)
            return result
        setattr(targetCls, methodName, _afterReturning)


    @staticmethod
    def afterThrowing(targetCls, methodName, wrapper):
        if not hasattr(targetCls, methodName):
            return
        target = getattr(targetCls, methodName)
        aspect = AspectUtils._aspectInst.get(targetCls, None)
        def _afterThrowing(inst, *args, **kwargs):
            try:
                result = target(inst, args, kwargs)
            except Exception as e:
                wrapper(aspect, inst, e, args, kwargs)
                raise e
            else:
                wrapper(aspect, inst, None, *args, **kwargs)
                return result
        setattr(targetCls, methodName, _afterThrowing)


    @staticmethod
    def replace(targetCls, methodName, wrapper):
        if not hasattr(targetCls, methodName):
            return
        target = getattr(targetCls, methodName)
        aspect = AspectUtils._aspectInst.get(targetCls, None)
        def _replace(inst, *args, **kwargs):
            return wrapper(aspect, inst, target, args, kwargs)
        setattr(targetCls, methodName, _replace)



def Aspect(target):
    # type: (type) -> type
    def wrapper(cls):
        aspectInst = cls()
        # 只允许注册一次，之后的更改无效
        if cls in AspectUtils._aspectInst:
            return cls
        AspectUtils._aspectInst[cls] = aspectInst
        for method in AnnotationHelper.findAnnotatedMethods(cls, ASPECT):
            aspect, methodName = AnnotationHelper.getAnnotation(method, ASPECT)
            if aspect == Aspects.Before:
                AspectUtils.before(target, methodName, method)
            elif aspect == Aspects.After:
                AspectUtils.after(target, methodName, method)
            elif aspect == Aspects.AfterReturning:
                AspectUtils.afterReturning(target, methodName, method)
            elif aspect == Aspects.AfterThrowing:
                AspectUtils.afterThrowing(target, methodName, method)
            elif aspect == Aspects.Replace:
                AspectUtils.replace(target, methodName, method)
        return cls
    return wrapper