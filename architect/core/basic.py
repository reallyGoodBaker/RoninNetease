import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
import threading

class Location:
    def __init__(self, pos, dim):
        self.pos = pos
        self.dim = dim

__threads = {}

def isServer():
    curId = threading.current_thread().ident
    if curId in __threads:
        return __threads[curId]
    else:
        _isServer = clientApi.GetLocalPlayerId() == '-1'
        __threads[threading.current_thread().ident] = _isServer
        return _isServer

def getComponentCls():
    if isServer():
        return serverApi.GetComponentCls()
    else:
        return clientApi.GetComponentCls()

def getGoalCls():
    return serverApi.GetCustomGoalCls()

def serverTick():
    return serverApi.GetServerTickTime()

compServer = serverApi.GetEngineCompFactory()
compClient = clientApi.GetEngineCompFactory()

localPlayer = lambda: clientApi.GetLocalPlayerId() # 不要在服务器端使用

defaultFilters = {
    "any_of": [
        {
            "subject" : "other",
            "test" :  "is_family",
            "value" :  "player"
        },
        {
            "subject" : "other",
            "test" :  "is_family",
            "value" :  "mob"
        }
    ]
}