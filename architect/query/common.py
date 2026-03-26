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


def Query(*compCls, **kwargs):
    """
    使用 Query 查询时，`self` 为 `entityId` 而不是类实例
    :param *compCls: 组件类或组件类名
    :param required: 必须包含的组件, 不会包含在查询结果中
    :param excluded: 必须排除的组件, 不会包含在查询结果中
    请一定要搭配 Sched.Tick() 或 Sched.Render() 使用
    """
    required = kwargs.get('required', [])
    excluded = kwargs.get('excluded', [])
    def decorator(fn):
        def wrapper(_):
            for entityId in getEntities():
                comps = getComponentWithQuery(entityId, compCls, required, excluded)
                if comps:
                    return fn(entityId, *comps)
        return wrapper
    return decorator


def QueryWithSelf(*compCls, **kwargs):
    """
    使用 Query 查询时，`self` 为类实例
    :param *compCls: 组件类或组件类名
    :param required: 必须包含的组件, 不会包含在查询结果中
    :param excluded: 必须排除的组件, 不会包含在查询结果中
    请一定要搭配 Sched.Tick() 或 Sched.Render() 使用
    """
    required = kwargs.get('required', [])
    excluded = kwargs.get('excluded', [])
    def decorator(fn):
        def wrapper(inst):
            for entityId in getEntities():
                comps = getComponentWithQuery(entityId, compCls, required, excluded)
                if comps:
                    return fn(inst, entityId, *comps)
        return wrapper
    return decorator