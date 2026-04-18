from ..core.annotation import AnnotationHelper
from ..conf import UI_DEF, UI_SINK, UI_NAMESPACE, UI_SCREEN, UI_HUD, UI_GESTURE
from ..event import EventSignal, EventTarget
from ..core.ref import Ref
from ..core.basic import clientApi
from ..level.client import LevelClient
from ..core.subsystem import ClientSubsystem, SubsystemManager, subsystem

from .gesture import GestureBinder, TouchEvents

class SinkContext(object):
    contextStack = [] # type: list[SinkContext]

    @staticmethod
    def stackTop():
        if len(SinkContext.contextStack) > 0:
            return SinkContext.contextStack[-1]
        return None

    def __init__(self, initiator):
        self.deps = [] # type: list[EventSignal]
        self._initiator = initiator
        SinkContext.contextStack.append(self)
        initiator()
        SinkContext.contextStack.pop()

    def _removeDepListeners(self):
        for dep in self.deps:
            dep.off(self._initiator)

    def __enter__(self):
        return self

    def recordDep(self, dep, value):
        # type: (EventSignal, object) -> None
        if dep in self.deps:
            return
        self.deps.append(dep)
        dep.on(self._initiator)


def UiDef(uiDef):
    def decorator(cls):
        AnnotationHelper.addAnnotation(cls, UI_DEF, uiDef)
        return cls
    return decorator


def AutoCreate(cls):
    cls._handleAutoCreate()
    return cls


def Screen(cls):
    AnnotationHelper.addAnnotation(cls, UI_SCREEN, True)
    return cls


def Hud(cls):
    AnnotationHelper.addAnnotation(cls, UI_HUD, True)
    return cls


def Sink(method):
    AnnotationHelper.addAnnotation(method, UI_SINK, True)
    return method


def signal(defaultValue=None, updater=None):
    # type: (object, function) -> tuple[function, function]
    val = Ref(defaultValue)
    dep = EventSignal()
    def getter():
        top = SinkContext.stackTop()
        if top:
            top.recordDep(dep, val.value)
        return val.value
    def setter(v):
        if updater:
            newVal = updater(v, val.value)
            dep.emit()
            val.value = newVal
        else:
            if v != val.value:
                dep.emit()
                val.value = v
    return (getter, setter)


def reactive(obj):
    # type: (object) -> tuple[function, function]
    """
    仅用于新式类 (继承自 object)
    """
    getVal, setVal = signal()
    def wrapSetattr(obj):
        objClass = obj.__class__
        previous = objClass.__setattr__
        def newSetattr(self, name, value):
            setVal(value)
            previous(self, name, value)
        objClass.__setattr__ = newSetattr
    wrapSetattr(obj)
    return (getVal, setVal)


ScreenNode = clientApi.GetScreenNodeCls()
class UiSubsystem(ScreenNode, ClientSubsystem, EventTarget):
    def __init__(self, engine, system, params):
        manager = SubsystemManager.getInstance()
        ScreenNode.__init__(self, engine, system, params)
        ClientSubsystem.__init__(self, manager.system, manager.engine, manager.sysName)
        EventTarget.__init__(self)
        manager.addSubsystemInst(self)
        self.params = params
        self.rootControl = None
        self._foundControls = {}
        self._sinks = {} # type: dict[function, SinkContext]

    @classmethod
    def _handleAutoCreate(cls):
        def createAsync():
            isScreen = AnnotationHelper.getAnnotation(cls, UI_SCREEN)
            isHud = AnnotationHelper.getAnnotation(cls, UI_HUD)
            cls.defineUi(AnnotationHelper.getAnnotation(cls, UI_DEF))
            if isScreen:
                subsystem.addListener(
                    'UiInitFinished',
                    lambda: cls.pushScreen()
                )
            elif isHud:
                subsystem.addListener(
                    'UiInitFinished',
                    lambda: cls.getOrCreate(isHud=True)
                )
            else:
                subsystem.addListener(
                    'UiInitFinished',
                    lambda: cls.create(isHud=False)
                )
        LevelClient.getInstance().game.AddTimer(0, createAsync)

    ns = UI_NAMESPACE
    inst = None

    def _initGesture(self):
        for method in AnnotationHelper.findAnnotatedMethods(self, UI_GESTURE):
            type, controlPath = AnnotationHelper.getAnnotation(method, UI_GESTURE)
            control = self.find(controlPath)
            if type in TouchEvents:
                control.asButton().AddTouchEventParams()
            GestureBinder[type](control, method.__get__(self))

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
        params['pushScreen'] = True
        ui = clientApi.PushScreen(cls.ns, cls.__name__, params)
        cls.inst = ui
        return ui

    def find(self, path):
        if path in self._foundControls:
            return self._foundControls[path]
        else:
            ctrl = self.GetBaseUIControl(path)
            self._foundControls[path] = ctrl
            return ctrl

    def findByName(self, name):
        return self.rootControl.GetChildByName(name)

    def _handleGamepadBack(self, ev):
        if not self.GetIsHud() and ev.key == 2 and ev.isDown:
            self._performBackPressed()

    def _handleKeyboardBack(self, ev):
        if not self.GetIsHud() and ev.key == '27' and ev.isDown:
            self._performBackPressed()

    def _initSinks(self):
        for method in AnnotationHelper.findAnnotatedMethods(self, UI_SINK):
            initiator = method.__get__(self)
            ctx = SinkContext(initiator)
            self._sinks[method] = ctx

    def _removeSinks(self):
        for method in AnnotationHelper.findAnnotatedMethods(self, UI_SINK):
            ctx = self._sinks.get(method)
            if ctx:
                ctx._removeDepListeners()

    def Create(self):
        self.rootControl = self.GetBaseUIControl('/')
        self.onCreate()
        self.listen('OnBackButtonReleaseClientEvent', self._performBackPressed)
        self.listen('OnGamepadKeyPressClientEvent', self._handleGamepadBack)
        self.listen('OnKeyPressInGame', self._handleKeyboardBack)
        self._initSinks()
        self._initGesture()

    def Destroy(self):
        self._removeSinks()
        self.unlisten('OnBackButtonReleaseClientEvent', self._performBackPressed)
        self.unlisten('OnGamepadKeyPressClientEvent', self._handleGamepadBack)
        self.unlisten('OnKeyPressInGame', self._handleKeyboardBack)
        self.onDestroy()

    def remove(self):
        if self.params.get('pushScreen'):
            clientApi.PopScreen()
        else:
            self.SetRemove()

    def _performBackPressed(self, *_):
        shouldPrevent = bool(self.onBackPressed())
        if not shouldPrevent and not self.GetIsHud():
            self.remove()

    def onCreate(self):
        pass

    def onBackPressed(self):
        # type: () -> bool
        pass

    def onDestroy(self):
        pass

