import time
import threading

import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi

from .basic import isServer, Location
from .level.server import LevelServer
from .component import registerComponents
from .event.client import event as eventClient
from .event.server import event as eventServer
from .annotation import AnnotationHelper
from .scheduler import Scheduler, Sched, SimpleFixedScheduler
from .conf import UI_NAMESPACE, EVENT_LISTENER, CUSTOM_EVENT, SYSTEM_SCHED_ANNO, TIMER_TASK

SYSTEM_CLIENT_NAME = '_ShadowSystemClient'
SYSTEM_SERVER_NAME = '_ShadowSystemServer'

class EventListener:
    def __init__(self, evType, fn):
        self.evType = evType
        self.fn = fn
        setattr(self, '<lambda>', self.fn)


class SubsystemManager:
    registeredSubsystems = []
    client = None
    server = None
    rawEngine = None
    rawSysName = None
    clientSubs = {}
    serverSubs = {}
    clientListeners = []
    serverListeners = []
    renderTickSched = Scheduler()
    clientTickSched = Scheduler()
    serverTickSched = Scheduler()

    @staticmethod
    def getInst():
        return SubsystemManager.server if isServer() else SubsystemManager.client
    
    @staticmethod
    def createClientSystem(engine, sysName, clsPath):
        """
        @deprecated
        """
        manager = SubsystemManager(
            clientApi.RegisterSystem(engine, sysName, clsPath),
            engine, sysName
        )
        manager.rawEngine = clientApi.GetEngineNamespace()
        manager.rawSysName = clientApi.GetEngineSystemName()
        SubsystemManager.client = manager
        return manager

    @staticmethod
    def createServerSystem(engine, sysName, clsPath):
        """
        @deprecated
        """
        manager = SubsystemManager(
            serverApi.RegisterSystem(engine, sysName, clsPath),
            engine, sysName
        )
        manager.rawEngine = serverApi.GetEngineNamespace()
        manager.rawSysName = serverApi.GetEngineSystemName()
        SubsystemManager.server = manager
        return manager

    @classmethod
    def createClient(cls, engine, sysName):
        manager = clientApi.GetSystem(engine, sysName) or SubsystemManager(
            clientApi.RegisterSystem(engine, sysName, cls.__module__ + '.' + SYSTEM_CLIENT_NAME),
            engine, sysName
        )
        manager.rawEngine = clientApi.GetEngineNamespace()
        manager.rawSysName = clientApi.GetEngineSystemName()
        SubsystemManager.client = manager
        return manager

    @classmethod
    def createServer(cls, engine, sysName):
        manager = serverApi.GetSystem(engine, sysName) or SubsystemManager(
            serverApi.RegisterSystem(engine, sysName, cls.__module__ + '.' + SYSTEM_SERVER_NAME),
            engine, sysName
        )
        manager.rawEngine = serverApi.GetEngineNamespace()
        manager.rawSysName = serverApi.GetEngineSystemName()
        SubsystemManager.server = manager
        return manager


    def __init__(self, system, engine, sysName):
        self.engine = engine
        self.sysName = sysName
        self.system = system

        if isServer():
            LevelServer.game.AddTimer(0, lambda: self.appendAllSubsystems(True))
        else:
            from .level.client import LevelClient
            LevelClient.getInst().game.AddTimer(0, lambda: self.appendAllSubsystems(False))


    def getSubsystems(self):
        return self.clientSubs if isServer() else self.serverSubs


    def appendAllSubsystems(self, isHost):
        for subsystemCls in SubsystemManager.registeredSubsystems:
            self.addSubsystem(subsystemCls)

        SubsystemManager.unregisterSubsystems()
        registerComponents(isHost)
        self._callReady(isHost)
        self.startTicking(isHost)


    def _callReady(self, isServer):
        subs = self.clientSubs if isServer else self.serverSubs
        for v in subs.values():
            if hasattr(v, 'onReady'):
                v.onReady()


    def startTicking(self, isServer):
        if isServer:
            self.system.ListenForEvent(
                self.rawEngine,
                self.rawSysName,
                'OnScriptTickServer',
                self,
                self.tickServer
            )
        else:
            self.system.ListenForEvent(
                self.rawEngine,
                self.rawSysName,
                'OnScriptTickClient',
                self,
                self.tickClient
            )
            self.system.ListenForEvent(
                self.rawEngine,
                self.rawSysName,
                'GameRenderTickEvent',
                self,
                self.tickRender
            )


    def addSubsystem(self, subsystemCls):
        subSys = subsystemCls(self.system, self.engine, self.sysName)
        self.addSubsystemInst(subSys)
        print('[INFO] {} Subsystem "{}" has been initialized'.format('Server' if isServer() else 'Client', subSys.__class__.__name__))


    def addSubsystemInst(self, subsystem):
        self.getSubsystems()[subsystem.__class__.__name__] = subsystem
        subsystem._init()


    def getSubsystem(self, subsystemCls):
        # type: (object) -> 'Subsystem'
        return self.getSubsystems().get(subsystemCls.__name__)
    

    def getSubsystemByName(self, name):
        # type: (str) -> 'Subsystem'
        return self.getSubsystems().get(name)


    def removeSubsystem(self, subsystemCls):
        subSystems = self.getSubsystems()
        subSys = subSystems[subsystemCls.__name__]
        if hasattr(subSys, 'onDestroy'):
            subSys.onDestroy()
        del subSystems[subsystemCls.__name__]


    @staticmethod
    def registerSubsystem(subsystem):
        inst = SubsystemManager.getInst()
        if not inst:
            SubsystemManager.registeredSubsystems.append(subsystem)
        else:
            inst.addSubsystem(subsystem)


    @staticmethod
    def unregisterSubsystems():
        SubsystemManager.registeredSubsystems = []


    lastTickTimeServer = time.time()
    lastTickTime = time.time()
    lastFrameTime = time.time()

    def tickServer(self):
        currentTime = time.time()
        dt = currentTime - self.lastTickTimeServer

        for obj in self.getSubsystems().values():
            if obj.canTick:
                obj.onUpdate(dt)
                obj.ticks += 1

        self.lastTickTimeServer = currentTime
        SubsystemManager.serverTickSched.executeSequence()


    def tickClient(self):
        currentTime = time.time()
        dt = currentTime - self.lastTickTime

        for obj in self.getSubsystems().values():
            if obj.canTick:
                obj.onUpdate(dt)
                obj.ticks += 1

        self.lastTickTime = currentTime
        SubsystemManager.clientTickSched.executeSequence()

    def tickRender(self, _):
        currentTime = time.time()
        dt = max(1e-5, currentTime - self.lastFrameTime)
        self.lastFrameTime = currentTime

        for obj in self.getSubsystems().values():
            if obj.canTick:
                obj.onRender(dt)

        SubsystemManager.renderTickSched.executeSequence()

    def addListener(self, event, fn, isCustomEvent=False):
        listeners = self.serverListeners if isServer() else self.clientListeners
        listener = EventListener(event, fn)
        if isCustomEvent:
            self.system.ListenForEvent(
                self.engine,
                self.sysName,
                event,
                listener,
                listener.fn
            )
        else:
            self.system.ListenForEvent(
                self.rawEngine,
                self.rawSysName,
                event,
                listener,
                listener.fn
            )
        listeners.append(listener)

    def removeListener(self, event, fn):
        listeners = self.serverListeners if isServer() else self.clientListeners
        for listener in listeners:
            if listener.fn == fn:
                self.system.UnListenForEvent(
                    self.rawEngine,
                    self.rawSysName,
                    event,
                    listener,
                    listener.fn
                )
                listeners.remove(listener)


class subsystem:

    _firstSubsysClient = None
    _firstSubsysServer = None

    @staticmethod
    def _findFirstSubsystem():
        # type: () -> ClientSubsystem | ServerSubsystem
        if isServer():
            if not subsystem._firstSubsysServer:
                subsystem._firstSubsysServer = SubsystemManager.getInst().getSubsystems().values()[0]
            return subsystem._firstSubsysServer
        else:
            if not subsystem._firstSubsysClient:
                subsystem._firstSubsysClient = SubsystemManager.getInst().getSubsystems().values()[0]
            return subsystem._firstSubsysClient

    @staticmethod
    def sendServer(event, data):
        client = subsystem._findFirstSubsystem() # type: ClientSubsystem
        client.sendServer(event, data)

    @staticmethod
    def sendClient(target, event, data):
        server = subsystem._findFirstSubsystem() # type: ServerSubsystem
        server.sendClient(target, event, data)

    @staticmethod
    def sendAllClients(event, data):
        server = subsystem._findFirstSubsystem() # type: ServerSubsystem
        server.sendAllClients(event, data)

    @staticmethod
    def spawnServerEntity(template, location, rot, isNpc=False, isGlobal=False):
        # type: (str, Location, tuple[float, float], bool, bool) -> 'None'
        serverSubsys = subsystem._findFirstSubsystem() # type: ServerSubsystem
        return serverSubsys.spawnEntity(template, location, rot, isNpc, isGlobal)

    @staticmethod
    def spawnClientEntity(template, pos, rot):
        # type: (str|dict, tuple[float, float, float], tuple[float, float]) -> 'None'
        clientSubsys = subsystem._findFirstSubsystem() # type: ClientSubsystem
        return clientSubsys.spawnEntity(template, pos, rot)

    @staticmethod
    def spawnItem(itemCls, *args, **kwargs):
        serverSubsys = subsystem._findFirstSubsystem()
        return serverSubsys.spawnItem(itemCls, *args, **kwargs)


def SubsystemClient(subsystemCls):
    """
    Decorator to auto register subsystem class
    """
    if not isServer():
        SubsystemManager.registerSubsystem(subsystemCls)
    return subsystemCls


def SubsystemServer(subsystemCls):
    """
    Decorator to auto register subsystem class
    """
    if isServer():
        SubsystemManager.registerSubsystem(subsystemCls)
    return subsystemCls


def getSubsystemCls():
    return ServerSubsystem if isServer() else ClientSubsystem


class Subsystem:
    def __init__(self, system, engine, sysName):
        # type: (object, str, str) -> 'None'
        self.system = system
        self.engine = engine
        self.sysName = sysName
        self.ticks = 0
        self.canTick = False
        self.initialized = False

    def onUpdate(self, dt):
        """
        每tick调用

        需要设置 `canTick` 为 `True`
        """
        pass

    def onReady(self):
        """
        所有子系统初始化完毕后调用

        此时所有子系统已经创建完毕，可以通过 `getSubsystem` 获取其他子系统
        """
        pass

    def onInit(self):
        """
        当前子系统创建完毕后调用

        此时 `SubystemManager` 已经创建完毕
        """
        pass

    def onDestroy(self):
        pass

    @classmethod
    def getInstance(cls):
        # type: () -> Subsystem
        return SubsystemManager.getInst().getSubsystem(cls)

    def getHost(self):
        # type: () -> _ShadowSystemServer | _ShadowSystemClient
        return self.system
    
    def getEngine(self):
        # type: () -> str
        return self.engine
    
    def getSysName(self):
        # type: () -> str
        return self.sysName
    
    def on(self, eventName, handler, isCustomEvent=True):
        # type: (str, function, bool) -> str
        return self._addListener(eventName, handler, isCustomEvent)

    def off(self, eventName, handler, isCustomEvent=True):
        # type: (str, function, bool) -> str
        return self._removeListener(eventName, handler, isCustomEvent)

    def listen(self, eventName, handler):
        # type: (str, function) -> str
        return self._addListener(eventName, handler, False)

    def unlisten(self, eventName, handler):
        # type: (str, function) -> str
        return self._removeListener(eventName, handler, False)

    def broadcast(self, eventName, eventData):
        # type: (str, dict) -> str
        self.system.BroadcastEvent(eventName, eventData)

    def _addListener(self, eventType, fn, isCustom=False):
        event = eventServer if isServer() else eventClient
        event(eventType, isCustom).addListener(fn)

    def _removeListener(self, eventType, fn, isCustom=False):
        event = eventServer if isServer() else eventClient
        event(eventType, isCustom).removeListener(fn)

    def _addListeners(self):
        methods = AnnotationHelper.findAnnotatedMethods(self, EVENT_LISTENER)
        for method in methods:
            eventType = AnnotationHelper.getAnnotation(method, EVENT_LISTENER)
            isCustomEvent = AnnotationHelper.getAnnotation(method, CUSTOM_EVENT) or False
            instMethod = method.__get__(self)
            self._addListener(eventType, instMethod, isCustomEvent)

    def _addSchedMethods(self):
        methods = AnnotationHelper.findAnnotatedMethods(self, SYSTEM_SCHED_ANNO)
        for method in methods:
            schedType, schedName = AnnotationHelper.getAnnotation(method, SYSTEM_SCHED_ANNO)
            instMethod = method.__get__(self)
            _isServer = isServer()
            if schedType == Sched.TYPE_RENDER:
                if _isServer:
                    continue
                SubsystemManager.renderTickSched.addTask(schedName, instMethod)
            elif schedType == Sched.TYPE_TICK:
                sched = SubsystemManager.serverTickSched if _isServer else SubsystemManager.clientTickSched
                sched.addTask(schedName, instMethod)
            elif schedType == Sched.TYPE_FIXED:
                sched = self._addFixedSched(schedName, instMethod)

    def _init(self):
        self._fixedSchedsToAdd = {} # type: dict[str, function]
        self.fixedSchedulers = {} # type: dict[str, SimpleFixedScheduler]
        self._addListeners()
        self._addSchedMethods()
        self.onInit()
        self.initialized = True

    def _addFixedSched(self, schedName, method):
        schedList = self._fixedSchedsToAdd.get(schedName, [])
        schedList.append(method)
        self._fixedSchedsToAdd[schedName] = schedList
    
    def scheduleFixed(self, schedName, period=1):
        """
        添加一个固定频率的调度器
        不要在使用注解注册的 Subsystem.onInit 调用, 此时游戏还未初始化
        """
        sched = SimpleFixedScheduler(period)
        self.fixedSchedulers[schedName] = sched
        schedTasks = self._fixedSchedsToAdd.pop(schedName, [])
        for task in schedTasks:
            sched.scheduler.addTask(TIMER_TASK, task)
        sched.start()
        return sched

    def stopFixed(self, schedName):
        sched = self.fixedSchedulers.pop(schedName, None)
        if sched:
            sched.cancel()
            return True
        return False


class ServerSubsystem(Subsystem):
    def __init__(self, system, engine, sysName):
        # type: (object, str, str) -> 'None'
        Subsystem.__init__(self, system, engine, sysName)

    def sendAllClients(self, eventName, eventData):
        self.system.BroadcastToAllClient(eventName, eventData)

    def sendClient(self, targetIds, eventName, eventData):
        if type(targetIds) == str or type(targetIds) == int:
            self.system.NotifyToClient(targetIds, eventName, eventData)
            return

        self.system.NotifyToMultiClients(targetIds, eventName, eventData)

    def spawnEntity(self, template, location, rot, isNpc=False, isGlobal=False):
        if type(template) == str:
            return self.system.CreateEngineEntityByTypeStr(template, location.pos, rot, dimensionId=location.dim, isNpc=isNpc, isGlobal=isGlobal)
        elif type(template) == dict:
            return self.system.CreateEngineEntityByNBT(template, location.pos, rot, dimensionId=location.dim, isNpc=isNpc, isGlobal=isGlobal)
        return None
        
    def destroyEntity(self, entityId):
        return self.system.DestroyEntity(entityId)
    
    def spawnItem(self, itemDict, location):
        return self.system.CreateEngineItemEntity(itemDict, dimensionId=location.dim, pos=location.pos)


class ClientSubsystem(Subsystem):

    def sendServer(self, eventName, eventData):
        self.system.NotifyToServer(eventName, eventData)

    def spawnEntity(self, typeStr, pos, rot):
        if type(typeStr) == str:
            return self.system.CreateClientEntityByTypeStr(typeStr, pos, rot)
        return None
    
    def onRender(self, dt):
        pass
    
    def destroyEntity(self, entityId):
        self.system.DestroyClientEntity(entityId)

    def createSfx(self, path, pos=None, rot=None, scale=None):
        return self.system.CreateEngineSfx(path, pos, rot, scale)
    
    def createParticle(self, path, pos):
        return self.system.CreateEngineParticle(path, pos)
    
    def createEffectBind(self, path, bindEntity, aniName):
        return self.system.CreateEngineEffectBind(path, bindEntity, aniName)
    
    def destroySfx(self, entityId):
        return self.system.DestroyEntity(entityId)


ScreenNode = clientApi.GetScreenNodeCls()
class UiSubsystem(ScreenNode, ClientSubsystem):
    def __init__(self, engine, system, params):
        manager = SubsystemManager.getInst()
        ScreenNode.__init__(self, engine, system, params)
        ClientSubsystem.__init__(self, manager.system, manager.engine, manager.sysName)
        manager.addSubsystemInst(self)

    ns = UI_NAMESPACE
    inst = None

    @classmethod
    def defineUi(cls, uiDef):
        return clientApi.RegisterUI(
            cls.ns,
            cls.__name__,
            cls.__module__ + '.' + cls.__name__,
            uiDef
        )
    
    @classmethod
    def getOrCreate(cls, **params):
        if cls.inst:
            return cls.inst

        ui = clientApi.CreateUI(cls.ns, cls.__name__, params)
        cls.inst = ui
        return ui
    
    @classmethod
    def create(cls, **params):
        ui = clientApi.CreateUI(cls.ns, cls.__name__, params)
        return ui
    
    @classmethod
    def pushScreen(cls, **params):
        ui = clientApi.PushScreen(cls.ns, cls.__name__, **params)
        cls.inst = ui
        return ui


ServerSystem = serverApi.GetServerSystemCls()
ClientSystem = clientApi.GetClientSystemCls()

class _ShadowSystemServer(ServerSystem):
    def getManager(self):
        return SubsystemManager.getInst()

class _ShadowSystemClient(ClientSystem):
    def getManager(self):
        return SubsystemManager.getInst()


def createServer(engine, sysName):
    return SubsystemManager.createServer(engine, sysName)

def createClient(engine, sysName):
    return SubsystemManager.createClient(engine, sysName)