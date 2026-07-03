# -*- coding: utf-8 -*-
from ..component import getComponent, getComponentWithQuery
from ..component.core import _getCompIndex, EMPTY_SLOT
from ..core.annotation import AnnotationHelper
from ..core.log import warn as _log_warn, info as _log_info
from ..conf import COMPONENT_TAG
from functools import wraps


class _Query:
    def __init__(self, entityId, comps):
        # type: (str, list) -> None
        self.entityId = entityId
        self.comps = comps

    def iter(self):
        return getComponent(self.entityId, self.comps) or []
    
    def __enter__(self):
        result = getComponent(self.entityId, self.comps)
        if result is None:
            raise Exception()
        return result
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return True


def query(entityId, comps):
    # type: (int, list) -> _Query
    return _Query(entityId, comps) # type: ignore


class EntityId:
    pass

class ExtraArguments:
    pass

class ExtraArgDict:
    pass

FakeComponents = [EntityId, ExtraArguments, ExtraArgDict]

def _getQueryArgs(entityId, compClsSrc, required, excluded, args, kwargs, showFailReason=False):
    # type: (str, list, list, list, list, dict, bool) -> list | None
    compCls = compClsSrc[:]
    entityIdIndex = -1
    extraArgsIndex = -1
    extraArgDict = -1
    if EntityId in compCls:
        entityIdIndex = compCls.index(EntityId)
        compCls[entityIdIndex] = None
    if ExtraArguments in compCls:
        extraArgsIndex = compCls.index(ExtraArguments)
        compCls[extraArgsIndex] = None
    if ExtraArgDict in compCls:
        extraArgDict = compCls.index(ExtraArgDict)
        compCls[extraArgDict] = None
    result, mismatch = getComponentWithQuery(entityId, compCls, required, excluded)
    if mismatch:
        if showFailReason:
            _log_warn('required 或 excluded 不匹配: {}', mismatch.__name__)
        return None
    if EMPTY_SLOT in result:
        if showFailReason:
            missingComps = []
            for i, v in enumerate(result):
                if v == EMPTY_SLOT:
                    missingComps.append(compCls[i].__name__)
            _log_info('缺失的查询组件: {}', ', '.join(missingComps))
        return None
    if entityIdIndex >= 0:
        result[entityIdIndex] = entityId
    if extraArgsIndex >= 0:
        result[extraArgsIndex] = args
    if extraArgDict >= 0:
        result[extraArgDict] = kwargs
    return result


def _isCompAllSingleton(compCls):
    # type: (list) -> bool
    singletonCount = 0
    compSize = len(compCls)
    for comp in compCls:
        if type(comp) == str:
            return False
        if comp == EntityId:
            return False
        if AnnotationHelper.getAnnotation(comp, COMPONENT_TAG).get('singleton'): # type: ignore
            singletonCount += 1
    return singletonCount == compSize


def Query(*compCls, **options):
    """
    Args:
        compCls (list[type[BaseCompServer|BaseCompClient]]): 组件类或组件类名
        required (list[type[BaseCompServer|BaseCompClient]]): 必须包含的组件, 不会包含在查询结果中
        excluded (list[type[BaseCompServer|BaseCompClient]]): 必须排除的组件, 不会包含在查询结果中
        showFailReason bool: 显示失败的原因

    使用 Query 查询时，`self` 为 ~entityId字符串~ 类实例,
    请一定要搭配 Sched.Tick() , Sched.Render() 等调度装饰器使用，否则不会执行。
    （不再使用 entityId 的理由是，这样做更符合直觉，且组件可以自行缓存 entityId）

    可以使用伪组件 ``EntityId``、``ExtraArguments``、``ExtraArgDict``
    来分别获取 *组件绑定的实体ID* ，*传入方法的参数列表* ，
    以及 *传入方法的参数字典* ，其中伪组件的位置没有要求。

    被这个装饰器装饰后，函数不会正常接收参数，而是在查询过程中动态注入参数，
    请不要尝试在子系统类中使用 self.xxx 调用被这个装饰器装饰的方法，
    除非你非常了解动态参数注入是如何实现的。

    **注意**：无法支持此版本之前的代码，请重构代码以使用此版本，重构方法为导入伪组件 `EntityId`,
    在参数列表的 self 后面加入 `id, ` 将之前代码中使用的self替换成id
    """
    required = options.get('required', [])
    excluded = options.get('excluded', [])
    showFailReason = options.get('showFailReason', False)
    def decorator(fn):
        isAllSingleton = _isCompAllSingleton(compCls) # type: ignore
        # 提取真实组件名 (过滤掉 EntityId 等伪组件), 用于索引查询
        _targetNames = [
            c for c in compCls
            if c not in FakeComponents
        ]

        @wraps(fn)
        def wrapper(inst, *args, **kwargs):
            _compList = list(compCls)
            if isAllSingleton:
                args = _getQueryArgs(None, _compList, required, excluded, args, kwargs, showFailReason) # type: ignore
                if args:
                    fn(inst, *args)
            else:
                # 从组件反向索引获取候选实体, 避免全量遍历
                candidateEntities = _getCompIndex().queryEntities(
                    _targetNames, required, excluded
                )
                # if fn.__name__ == 'onJump':
                #     print candidateEntities
                for entityId in candidateEntities:
                    if not entityId:
                        continue
                    comps = _getQueryArgs(entityId, _compList, required, excluded, args, kwargs, showFailReason) # type: ignore
                    if comps:
                        fn(inst, *comps)
        return wrapper
    return decorator


def Track(message=None):
    def _tracker(method):
        @wraps(method)
        def modified(self, *args, **kwargs):
            msg = message or "Called: '{}.{}'".format(self.__class__.__name__, method.__name__)
            _log_info(msg)
            return method(self, *args, **kwargs)
        return modified
    return _tracker
