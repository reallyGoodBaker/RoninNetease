from ..component import getComponent, getComponentWithQuery, getEntities


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
    return _Query(entityId, comps)


class EntityId:
    pass

class ExtraArguments:
    pass

class ExtraArgDict:
    pass


def _getQueryArgs(entityId, compCls, required, excluded, args, kwargs):
    # type: (str, list, list, list, list, dict) -> list
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
    result = getComponentWithQuery(entityId, compCls, required, excluded)
    if not result:
        return None
    if entityIdIndex >= 0:
        result[entityIdIndex] = entityId
    if extraArgsIndex >= 0:
        result[extraArgsIndex] = args
    if extraArgDict >= 0:
        result[extraArgDict] = kwargs
    return result


def Query(*compCls, **options):
    """
    使用 Query 查询时，`self` 为类实例
    :param *compCls: 组件类或组件类名
    :param required: 必须包含的组件, 不会包含在查询结果中
    :param excluded: 必须排除的组件, 不会包含在查询结果中
    请一定要搭配 Sched.Tick() 或 Sched.Render() 使用
    """
    required = options.get('required', [])
    excluded = options.get('excluded', [])
    def decorator(fn):
        def wrapper(inst, *args, **kwargs):
            instMethod = fn.__get__(inst)
            for entityId in getEntities():
                comps = _getQueryArgs(entityId, list(compCls), required, excluded, args, kwargs)
                if comps:
                    return instMethod(*comps)
        return wrapper
    return decorator