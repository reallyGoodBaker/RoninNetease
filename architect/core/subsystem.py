import time

import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi

from .annotation import AnnotationHelper
from .scheduler import Scheduler, Sched, SimpleFixedScheduler
from .basic import isServer, Location
from .loader import __modname__, _loadPlugins, _notifyAddSubsystem, _notifyRemoveSubsystem, modConf

from ..level.server import LevelServer
from ..component.core import _registerCompsIntoGame, getOrCreateSingletonComponent
from ..event.client import event as eventClient
from ..event.server import event as eventServer
from ..conf import EVENT_LISTENER, CUSTOM_EVENT, SYSTEM_SCHED_ANNO, SCHED_EVENT


SYSTEM_CLIENT_NAME = '_ShadowSystemClient'
SYSTEM_SERVER_NAME = '_ShadowSystemServer'


class EventListener:
    def __init__(self, evType, fn):
        self.evType = evType
        self.fn = fn
        setattr(self, fn.__name__, self.fn)


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
    def _relative(path):
        # type: (str) -> str
        return __modname__ + '.' + path


    @staticmethod
    def getInstance():
        return SubsystemManager.server if isServer() else SubsystemManager.client


    @classmethod
    def createClient(cls):
        getConf = modConf()
        engine = getConf('MOD_ENGINE_NAME')
        sysName = getConf('MOD_SYSTEM_NAME')
        modules = getConf('MOD_CLIENT_MODULES')
        existed = clientApi.GetSystem(engine, sysName)
        manager = existed.getManager() if existed else SubsystemManager(
            clientApi.RegisterSystem(engine, sysName, cls.__module__ + '.' + SYSTEM_CLIENT_NAME),
            engine, sysName
        )
        for clientModule in modules:
            clientApi.ImportModule(cls._relative(clientModule))
        manager.rawEngine = clientApi.GetEngineNamespace()
        manager.rawSysName = clientApi.GetEngineSystemName()
        SubsystemManager.client = manager
        # 在manager之前初始化，否则无法监听组件注册和子系统变更
        _loadPlugins(manager)
        manager._initManager(False)
        return manager


    @classmethod
    def createServer(cls):
        try:
            from ...conf import MOD_ENGINE_NAME, MOD_SYSTEM_NAME
        except ImportError:
            raise ImportError('请在 {} 文件夹中创建 conf.py 文件，并定义 MOD_ENGINE_NAME 和 MOD_SYSTEM_NAME'.format(__modname__))
        engine = MOD_ENGINE_NAME
        sysName = MOD_SYSTEM_NAME
        existed = serverApi.GetSystem(engine, sysName)
        manager = existed.getManager() if existed else SubsystemManager(
            serverApi.RegisterSystem(engine, sysName, cls.__module__ + '.' + SYSTEM_SERVER_NAME),
            engine, sysName
        )
        manager.rawEngine = serverApi.GetEngineNamespace()
        manager.rawSysName = serverApi.GetEngineSystemName()
        SubsystemManager.server = manager
        def _initLater(_):
            # 在manager之前初始化，否则无法监听组件注册和子系统变更
            getConf = modConf()
            for serverModule in getConf('MOD_SERVER_MODULES'):
                serverApi.ImportModule(cls._relative(serverModule))
            _loadPlugins(manager)
            manager._initManager(True)
        listener = EventListener('LoadServerAddonScriptsAfter', _initLater)
        manager.system.ListenForEvent(
            manager.rawEngine,
            manager.rawSysName,
            'LoadServerAddonScriptsAfter',
            listener,
            listener.fn
        )
        return manager


    def __init__(self, system, engine, sysName):
        self.engine = engine
        self.sysName = sysName
        self.system = system
        setattr(system, 'getManager', lambda val=self: val)


    def getSubsystems(self):
        return self.clientSubs if isServer() else self.serverSubs
    

    def _record(self, inst):
        self.getSubsystems()[inst.__class__.__name__] = inst


    def _removeRecord(self, inst):
        self.getSubsystems().pop(inst.__class__.__name__, None)


    def _addAnnotatedSubsystems(self):
        for subsystemCls in SubsystemManager.registeredSubsystems:
            self.addSubsystem(subsystemCls)
        SubsystemManager.unregisterSubsystems()


    def _initManager(self, isHost):
        _registerCompsIntoGame(isHost)
        self._addAnnotatedSubsystems()
        self._callReady(isHost)
        self.startTicking(isHost)


    def _callReady(self, isServer):
        subs = self.clientSubs if isServer else self.serverSubs
        for v in subs.values():
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
        _notifyAddSubsystem(subSys)
        print('[INFO] {} Subsystem "{}" has been initialized'.format('Server' if isServer() else 'Client', subSys.__class__.__name__))


    def addSubsystemInst(self, subsystem):
        subsystem._init()


    def getSubsystem(self, subsystemCls):
        # type: (object) -> 'Subsystem'
        return self.getSubsystems().get(subsystemCls if type(subsystemCls) is str else subsystemCls.__name__)
    

    def getSubsystemByName(self, name):
        # type: (str) -> 'Subsystem'
        return self.getSubsystems().get(name)


    def removeSubsystem(self, subsystemCls):
        subSystems = self.getSubsystems()
        subSys = subSystems[subsystemCls.__name__]
        _notifyRemoveSubsystem(subSys)
        subSys._destroy()


    @staticmethod
    def registerSubsystem(subsystem):
        inst = SubsystemManager.getInstance()
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
                subsystem._firstSubsysServer = SubsystemManager.getInstance().getSubsystems().values()[0]
            return subsystem._firstSubsysServer
        else:
            if not subsystem._firstSubsysClient:
                subsystem._firstSubsysClient = SubsystemManager.getInstance().getSubsystems().values()[0]
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
    
    @staticmethod
    def addListener(event, fn, isCustomEvent=False):
        # type: (str, function, bool) -> str
        return subsystem._findFirstSubsystem()._addListener(event, fn, isCustomEvent)

    @staticmethod
    def removeListener(event, fn, isCustomEvent=False):
        # type: (str, function, bool) -> str
        return subsystem._findFirstSubsystem()._removeListener(event, fn, isCustomEvent)


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



class Subsystem(object):
    def __init__(self, system, engine, sysName):
        # type: (object, str, str) -> 'None'
        self.system = system        # type: _ShadowSystemServer | _ShadowSystemClient
        self.engine = engine        # type: str
        self.sysName = sysName      # type: str
        self.ticks = 0              # type: int
        self.canTick = False        # type: bool
        self.initialized = False    # type: bool

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
        if 1 > 2:
            return cls(None, None, None)
        return SubsystemManager.getInstance().getSubsystem(cls)

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

    def _removeListeners(self):
        methods = AnnotationHelper.findAnnotatedMethods(self, EVENT_LISTENER)
        for method in methods:
            eventType = AnnotationHelper.getAnnotation(method, EVENT_LISTENER)
            isCustomEvent = AnnotationHelper.getAnnotation(method, CUSTOM_EVENT) or False
            instMethod = method.__get__(self)
            self._removeListener(eventType, instMethod, isCustomEvent)

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
            schedType, schedFlag, opt = AnnotationHelper.getAnnotation(method, SYSTEM_SCHED_ANNO)
            instMethod = method.__get__(self)
            _isServer = isServer()
            if schedType == Sched.TYPE_RENDER:
                if _isServer:
                    continue
                SubsystemManager.renderTickSched.addTask(schedFlag, instMethod)
            elif schedType == Sched.TYPE_TICK:
                sched = SubsystemManager.serverTickSched if _isServer else SubsystemManager.clientTickSched
                sched.addTask(schedFlag, instMethod)
            elif schedType == Sched.TYPE_FIXED:
                schedulerName = opt['schedulerName']
                sched = self._addFixedSched(schedulerName, schedFlag, instMethod)
            elif schedType == Sched.TYPE_EVENT:
                isCustom = opt.get('isCustom')
                eventType = opt.get('eventType')
                self._handleSchedEvents(eventType, instMethod, isCustom, schedFlag)

    def _handleSchedEvents(self, eventType, instMethod, isCustom, schedFlag):
        schedKey = (eventType, isCustom)
        reader = getOrCreateSingletonComponent('EventReader')
        if not reader:
            return
        if schedKey not in self._schedEvents:
            self._schedEvents[schedKey] = ([], [])
            def handler(event):
                reader.ev = event
                for stage in self._schedEvents[schedKey]:
                    for fn in stage:
                        fn()
                reader.ev = None
            self.on(eventType, handler, isCustom)
        schedListeners = self._schedEvents[schedKey]
        targetList = schedListeners[0] if schedFlag == SCHED_EVENT else schedListeners[1]
        targetList.append(instMethod)

    def _removeSchedEvents(self):
        for schedKey, schedList in self._schedEvents.items():
            eventType, isCustom = schedKey
            for fn in schedList:
                self.off(eventType, fn, isCustom)

    def _removeSchedMethods(self):
        methods = AnnotationHelper.findAnnotatedMethods(self, SYSTEM_SCHED_ANNO)
        for method in methods:
            schedType, schedName = AnnotationHelper.getAnnotation(method, SYSTEM_SCHED_ANNO)
            if schedType == Sched.TYPE_RENDER:
                SubsystemManager.renderTickSched.removeTask(schedName)
            elif schedType == Sched.TYPE_TICK:
                sched = SubsystemManager.serverTickSched if isServer() else SubsystemManager.clientTickSched
                sched.removeTask(schedName)
            elif schedType == Sched.TYPE_FIXED:
                self.stopFixed(schedName)
            elif schedType == Sched.TYPE_EVENT:
                self._removeSchedEvents()

    def _init(self):
        SubsystemManager.getInstance()._record(self)
        self._fixedSchedsToAdd = {} # type: dict[str, function]
        self._schedEvents = {} # type: dict[str, tuple[list[function], list[function]]]
        self.fixedSchedulers = {} # type: dict[str, SimpleFixedScheduler]
        self._addListeners()
        self._addSchedMethods()
        self.onInit()
        self.initialized = True

    def _destroy(self):
        self.initialized = False
        self.onDestroy()
        self._removeSchedMethods()
        self._removeListeners()
        SubsystemManager.getInstance()._removeRecord(self)

    def _addFixedSched(self, schedulerName, schedFlag, method):
        schedList = self._fixedSchedsToAdd.get(schedulerName, [])
        schedList.append({
            'flag': schedFlag,
            'method': method
        })
        self._fixedSchedsToAdd[schedulerName] = schedList
    
    def scheduleFixed(self, schedName, period=1):
        """
        添加一个固定频率的调度器
        不要在使用注解注册的 Subsystem.onInit 调用, 此时游戏还未初始化
        """
        sched = SimpleFixedScheduler(period)
        self.fixedSchedulers[schedName] = sched
        schedTasks = self._fixedSchedsToAdd.pop(schedName, [])
        for config in schedTasks:
            task = config['method']
            schedFlag = config['flag']
            sched.scheduler.addTask(schedFlag, task)
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


ServerSystem = serverApi.GetServerSystemCls()
ClientSystem = clientApi.GetClientSystemCls()

class _ShadowSystemServer(ServerSystem):
    def getManager(self):
        return SubsystemManager.getInstance()

class _ShadowSystemClient(ClientSystem):
    def getManager(self):
        return SubsystemManager.getInstance()


def createServer():
    return SubsystemManager.createServer()

def createClient():
    return SubsystemManager.createClient()