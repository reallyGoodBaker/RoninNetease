from ..annotation import AnnotationHelper
from ..basic import isServer, clientApi, serverApi
from .common import _nativeCompGet
from ..conf import COMPONENT_NAMESPACE, COMPONENT_TAG

clientCompCls = []
serverCompCls = []

components = {}

def Component(persist=False):
    def decorator(cls):
        _isServer = isServer()
        clsList = serverCompCls if _isServer else clientCompCls
        # 标记类为组件
        AnnotationHelper.addAnnotation(cls, COMPONENT_TAG, {
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
    return AnnotationHelper.getAnnotation(cls, COMPONENT_TAG)


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

def createComponents(entityId, *clsList):
    result = []
    for cls in clsList:
        result.append(createComponent(entityId, cls))
    return result if len(result) > 1 else result

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
    
def _findNamedComp(entityId, name):
    # type: (str, str) -> object
    if name.startswith('#'):
        return _nativeCompGet(entityId, name)
    else:
        key = (entityId, name)
        if key in components:
            return components[key]
        else:
            return None

def getComponent(entityId, clsList, filter=None):
    # type: (str, list[type|str], function) -> list
    result = []
    for c in iter(clsList):
        compKey = c if type(c) == str else c.__name__
        comp = _findNamedComp(entityId, compKey)
        if filter is None or filter(comp, compKey):
            result.append(comp)
        else:
            return None
    return result

def getComponentWithQuery(entityId, targets, required=[], excluded=[]):
    if len(required) + len(excluded) > 0:
        def mapStr(obj):
            return obj if type(obj) == str else obj.__name__
        def _matcher(_, compName):
            inTargets = compName in map(mapStr, targets)
            inRequired = compName in map(mapStr, required)
            notExcluded = compName not in map(mapStr, excluded)
            return inTargets and inRequired and notExcluded
        return getComponent(entityId, targets, _matcher)
    else:
        return getComponent(entityId, targets)

def getEntities():
    entities = entitiesServer if isServer() else entitiesClient
    return list(entities.keys())


class BaseCompServer(serverApi.GetComponentCls()):
    def onCreate(self, entityId):
        pass

    def loadData(self, entityId):
        pass

class BaseCompClient(clientApi.GetComponentCls()):
    def onCreate(self, entityId):
        pass

    def loadData(self, entityId):
        pass