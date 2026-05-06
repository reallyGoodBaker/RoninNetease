from time import time

from ....compact import ClientSubsystem, SubsystemClient, getOneSingletonComponent, EventListener, localPlayerId
from ..utils.mappingContext import InputMapping
from ..utils.inputValue import InputValue
from ..utils.inputAction import InputAction
from ..utils.trigger import InputTrigger
from ..components.inputEx import InputExComponent
from ..enum import AccumulationBehavior, InputType, TriggerState, TriggerCombineType, InputState, IA_EVENT_PREFIX


class _TransState:
    Empty = 0
    Started = 1
    Triggered = 2
    Completed = 3
    Canceled = 4
    Ongoing = 5
    StartedAndTriggered = 6


_StateTransResultMapping = {
    (TriggerState.Empty, TriggerState.Empty):           (_TransState.Empty,                 InputState.Empty),
    (TriggerState.Empty, TriggerState.Ongoing):         (_TransState.Started,               InputState.Started),
    (TriggerState.Empty, TriggerState.Triggered):       (_TransState.StartedAndTriggered,   InputState.Triggered),
    (TriggerState.Ongoing, TriggerState.Empty):         (_TransState.Canceled,              InputState.Canceled),
    (TriggerState.Ongoing, TriggerState.Ongoing):       (_TransState.Ongoing,               InputState.Ongoing),
    (TriggerState.Ongoing, TriggerState.Triggered):     (_TransState.Triggered,             InputState.Triggered),
    (TriggerState.Triggered, TriggerState.Empty):       (_TransState.Completed,             InputState.Completed),
    (TriggerState.Triggered, TriggerState.Triggered):   (_TransState.Triggered,             InputState.Triggered),
    (TriggerState.Triggered, TriggerState.Ongoing):     (_TransState.Empty,                 InputState.Ongoing)
}


@SubsystemClient
class InputExClient(ClientSubsystem):

    def onInit(self):
        self.canTick = True
        self.inputMappings = [] # type: list[InputMapping]
        self._iaEvents = set()


    def enableMapping(self, name):
        mapping = InputMapping.get(name)
        if not mapping:
            return False
        self.inputMappings.append(mapping)
        if len(self.inputMappings):
            self.inputMappings.sort(key=lambda x: x.priority, reverse=True)
        return True
    

    def disableMapping(self, name):
        mapping = InputMapping.get(name)
        if not mapping:
            return False
        self.inputMappings.remove(mapping)
        if len(self.inputMappings):
            self.inputMappings.sort(key=lambda x: x.priority, reverse=True)
        return True


    def _updateMapping(self, mapping, inputEx, dt):
        # type: (InputMapping, InputExComponent, float) -> None
        inputEx.actionValues.clear()
        self._iaEvents.clear()
        for binding in mapping.bindings:
            value = inputEx.getInputValue(binding.inputType, binding.key) # type: InputValue
            modifiedValue = value.rawValue[:]
            for modifier in binding.modifiers:
                modifiedValue = modifier.doModify(modifiedValue)
            self._handleAction(value, inputEx, binding.action, modifiedValue, dt, binding.triggers)
        for actionName, transState in self._iaEvents:
            self._dispatchIAEvent(transState, actionName, inputEx)


    def _evalTriggers(self, dt, inputVal, prevState, mappingTriggers, actionTriggers):
        # type: (float, InputValue, TriggerState, list[InputTrigger], list[InputTrigger]) -> TriggerState
        """
        综合判断触发器状态
        规则: 默认为 Empty, 任意一个 Trigger 返回 Ongoing 时切换到 Ongoing,
        所有隐式 Trigger 返回 Triggered 且任意一个显式 Trigger 返回 Triggered 时切换到 Triggered,
        所有 Trigger 返回 Empty 时切换到 Empty
        """
        _ongoings = 0
        _emptyTriggers = 0
        _implicitsSize = 0
        _explicitsSize = 0
        _triggeredImplicits = 0
        _triggeredExplicits = 0
        allTriggers = mappingTriggers + actionTriggers

        if len(allTriggers) == 0:
            return TriggerState.Empty

        for trigger in allTriggers:
            if trigger.combineType == TriggerCombineType.And:
                _implicitsSize += 1
                triggerState = trigger.updateState(inputVal, dt)
                if triggerState == TriggerState.Ongoing:
                    _ongoings += 1
                elif triggerState == TriggerState.Triggered:
                    _triggeredImplicits += 1
                elif triggerState == TriggerState.Empty:
                    _emptyTriggers += 1
            elif trigger.combineType == TriggerCombineType.Or:
                _explicitsSize += 1
                triggerState = trigger.updateState(inputVal, dt)
                if triggerState == TriggerState.Ongoing:
                    _ongoings += 1
                elif triggerState == TriggerState.Triggered:
                    _triggeredExplicits += 1
                elif triggerState == TriggerState.Empty:
                    _emptyTriggers += 1

        curTriggerState = TriggerState.Empty
        # Trigger: And triggers 必须全部为 Triggered, Or 触发器只要有一个为 Triggered 即可
        if _triggeredImplicits == _implicitsSize and (_explicitsSize == 0 or _triggeredExplicits > 0):
            curTriggerState = TriggerState.Triggered
        # Ongoing: 只要有一个触发器为 Ongoing, 则为 Ongoing
        elif _ongoings > 0:
            curTriggerState = TriggerState.Ongoing
        else:
            curTriggerState = TriggerState.Empty

        return _StateTransResultMapping.get((prevState, curTriggerState), (InputState.Empty, InputState.Empty))


    def _dispatchIAEvent(self, transState, actionName, inputEx):
        # type: (_TransState, str, InputExComponent) -> None
        _, valVec = inputEx.actionValues[actionName]
        if transState == 0:
            return
        ia = InputAction.get(actionName)
        for modifier in ia.modifiers:
            valVec = modifier.doModify(valVec)
        value = InputValue.value(valVec, ia.valueType)
        evNamePrefix = IA_EVENT_PREFIX + actionName
        if transState == _TransState.StartedAndTriggered:
            self.broadcast(evNamePrefix + str(InputState.Started), { 'value': value })
            self.broadcast(evNamePrefix + str(InputState.Triggered), { 'value': value })
        else:
            self.broadcast(evNamePrefix + str(transState), { 'value': value })


    def _mixIAValue(self, ia, prevValue, value):
        # type: (InputAction, tuple[float, float, float], tuple[float, float, float]) -> tuple[float, float, float]
        if ia.accBehavior == AccumulationBehavior.Override:
            return value
        elif ia.accBehavior == AccumulationBehavior.Cumulative:
            px, py, pz = prevValue
            vx, vy, vz = value
            return (px + vx, py + vy, pz + vz)
        elif ia.accBehavior == AccumulationBehavior.HighestAbsValue:
            px, py, pz = prevValue
            vx, vy, vz = value
            return (
                px if abs(px) > abs(vx) else vx,
                py if abs(py) > abs(vy) else vy,
                pz if abs(pz) > abs(vz) else vz
            )


    def _handleAction(self, inputValue, inputEx, actionName, value, dt, mappingTriggers):
        # type: (InputValue, InputExComponent, str, tuple[float, float, float], float, list[InputTrigger]) -> None
        ia = InputAction.get(actionName) # type: InputAction
        if not ia:
            return

        prevState, actionValue = inputEx.actionValues.get(actionName, (TriggerState.Empty, (0.0, 0.0, 0.0)))
        transState, inputState = self._evalTriggers(dt, inputValue, prevState, mappingTriggers, ia.triggers)
        newActionValue = self._mixIAValue(ia, actionValue, value)
        inputEx.actionValues[actionName] = (inputState, newActionValue)
        self._iaEvents.add((actionName, transState))


    def updateMapping(self, deltaTime):
        inputEx = getOneSingletonComponent(InputExComponent)
        for mapping in self.inputMappings:
            self._updateMapping(mapping, inputEx, deltaTime)


    def onRender(self, dt):
        self.updateMapping(dt)


    @EventListener('OnKeyPressInGame')
    def onKeyboardPress(self, ev):
        key = int(ev.key)
        isDown = int(ev.isDown)
        inputEx = getOneSingletonComponent(InputExComponent)
        inputEx.updateInputValue(InputType.Key, key, (isDown, 0.0, 0.0))


    @EventListener('OnGamepadKeyPressClientEvent')
    def onGamepadPress(self, ev):
        button = ev.key
        isDown = int(ev.isDown)
        inputEx = getOneSingletonComponent(InputExComponent)
        inputEx.updateInputValue(InputType.Gamepad, button, (isDown, 0.0, 0.0))


    @EventListener('OnGamepadStickClientEvent')
    def onGamepadStick(self, ev):
        stick = ev.key
        x = ev.x
        y = ev.y
        inputEx = getOneSingletonComponent(InputExComponent)
        inputEx.updateInputValue(InputType.Axis, stick, (x, y, 0.0))


    @EventListener('OnGamepadTriggerClientEvent')
    def onGamepadTrigger(self, ev):
        key = ev.key
        value = ev.magnitude
        inputEx = getOneSingletonComponent(InputExComponent)
        inputEx.updateInputValue(InputType.Axis, key, (value, 0.0, 0.0))