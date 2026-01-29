from ..annotation import AnnotationHelper
from ..basic import isServer, clientApi, serverApi

COMPONENT_NAMESPACE = 'xxx_roninComponent_xxx'

clientCompCls = []
serverCompCls = []

components = {}

def Component(persist=False):
    def decorator(cls):
        _isServer = isServer()
        clsList = serverCompCls if _isServer else clientCompCls
        # 标记类为组件
        AnnotationHelper.addAnnotation(cls, '_component', {
            'persist': persist
        })

        clsList.append(cls)
        return cls

    return decorator

def registerComponents(isServer):
    clsList = serverCompCls if isServer else clientCompCls
    api = serverApi if isServer else clientApi
    for cls in clsList:
        result = api.RegisterComponent(COMPONENT_NAMESPACE, cls.__name__, cls.__module__ + '.' + cls.__name__)
        print('[INFO] Register component', cls.__name__, 'result:', result)


def getComponentAnnotation(cls):
    return AnnotationHelper.getAnnotation(cls, '_component')


def isPersistComponent(cls):
    ann = getComponentAnnotation(cls)
    return ann is not None and ann.get('persist', False)

entitiesServer = {}
entitiesClient = {}

def createComponent(entityId, cls):
    # print('create component', entityId, cls)
    api = serverApi if isServer() else clientApi
    comp = api.CreateComponent(entityId, COMPONENT_NAMESPACE, cls.__name__)
    components[(entityId, cls.__name__)] = comp
    if isPersistComponent(cls) and hasattr(comp, 'loadData'):
        comp.loadData(entityId)

    if hasattr(comp, 'onCreate'):
        comp.onCreate(entityId)

    entities = entitiesServer if isServer() else entitiesClient
    if entityId not in entities:
        entities[entityId] = 0
    entities[entityId] += 1
    return comp

def destroyComponent(entityId, cls):
    api = serverApi if isServer() else clientApi
    api.DestroyComponent(entityId, COMPONENT_NAMESPACE, cls.__name__)
    key = (entityId, cls)
    entities = entitiesServer if isServer() else entitiesClient
    if key in components:
        del components[key]
    if entityId in entities:
        entities[entityId] -= 1
        if entities[entityId] <= 0:
            del entities[entityId]

def getOneComponent(entityId, cls):
    comps = getComponent(entityId, [cls])
    if comps and len(comps) > 0:
        return comps[0]

def getComponent(entityId, clsList, filter=None):
    # type: (str, list[type], function) -> list
    result = []
    for c in iter(clsList):
        key = (entityId, c.__name__)
        if key in components:
            comp = components[key]
            if filter is None or filter(comp, c.__name__):
                result.append(components[key])
        else:
            return None
    return result

def getComponentWithQuery(entityId, targets, required=[], excluded=[]):
    if len(required) + len(excluded) > 0:
        def _matcher(_, compName):
            inTargets = compName in map(lambda cls: cls.__name, targets)
            inRequired = compName in map(lambda cls: cls.__name, required)
            notExcluded = compName not in map(lambda cls: cls.__name, excluded)
            return inTargets and inRequired and notExcluded
        return getComponent(entityId, targets, _matcher)
    else:
        return getComponent(entityId, targets)

def getEntities():
    entities = entitiesServer if isServer() else entitiesClient
    return list(entities.keys())


class BaseCompServer(serverApi.GetComponentCls()):
    def onCreate(self):
        pass

    def loadData(self, entityId):
        pass

class BaseCompClient(clientApi.GetComponentCls()):
    def onCreate(self):
        pass

    def loadData(self, entityId):
        pass