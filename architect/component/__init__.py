from .index import Component, registerComponents, getComponent, getComponentAnnotation, getEntities, isPersistComponent, createComponent, createSingletonComponent, destroyComponent, getOneComponent, getComponentWithQuery, getOrCreateComponent, getOrCreateSingletonComponent, getOneSingletonComponent, hasComponent, removeComponents, BaseCompClient, BaseCompServer
from ..basic import getComponentCls, serverApi, clientApi
from .common import NeC, NeS

class ClientComponent(clientApi.GetComponentCls()):
    def onCreate(self, entityId):
        pass

    def loadData(self, entityId):
        pass


class ServerComponent(serverApi.GetComponentCls()):
    def onCreate(self, entityId):
        pass

    def loadData(self, entityId):
        pass