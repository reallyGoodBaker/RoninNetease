from ....compact import ClientSubsystem, SubsystemClient, EventListener, getOneComponent, Sched, SchedUpdateFlags
from ..utils.mappingContext import InputMapping
from ..utils.inputValue import InputValue
from ..utils.inputAction import InputAction
from ..components.inputEx import InputExComponent
from ..enum import TriggerState, TriggerCombineType


@SubsystemClient
class InputExClient(ClientSubsystem):

    def onInit(self):
        self.canTick = True
        self.inputMappings = [] # type: list[InputMapping]


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
        for binding in mapping.bindings:
            value = inputEx.getInputValue(binding.inputType, binding.key) # type: InputValue
            shouldTrigger = True
            modifiedValue = value.rawValue[:]
            finalTriggerState = -1
            finalTrigger = None
            for trigger in binding.triggers:
                triggerState = trigger.updateState(value.rawValue, dt)
                if finalTriggerState < triggerState :
                    finalTriggerState = triggerState
                    finalTrigger = trigger
            if not shouldTrigger:
                continue
            for modifier in binding.modifiers:
                modifiedValue = modifier.doModify(modifiedValue)
            self._handleAction(inputEx, binding.action, modifiedValue, dt, finalTriggerState, finalTrigger.combineType)


    def _evalTrigger(self, mappingTriggerState, mappingTriggerCombineType, actionTriggerState, actionTriggerCombineType):
        pass 


    def _handleAction(self, inputEx, actionName, value, dt, mappingTriggerState, mappingTriggerCombineType):
        # type: (InputExComponent, str, tuple[float, float, float], float, TriggerState, TriggerCombineType) -> None
        ia = InputAction.get(actionName) # type: InputAction
        if not ia:
            return
        finalTriggerState = -1
        finalTrigger = None
        for trigger in ia.triggers:
            triggerState = trigger.updateState(value, dt)
            if triggerState > finalTriggerState:
                finalTriggerState = triggerState
                finalTrigger = trigger
        for modifier in ia.modifiers:
            value = modifier.doModify(value)
        prevTriggerState = inputEx.actionValues.get(actionName, (TriggerState.Empty, 0.0))[0]
        actionTriggerCombineType = finalTrigger.combineType
        inputEx.actionValues[actionName] = (finalTriggerState, value)


    def updateMapping(self, deltaTime):
        inputEx = getOneComponent(InputExComponent)
        for mapping in self.inputMappings:
            self._updateMapping(mapping, inputEx, deltaTime)


    def onRender(self, dt):
        self.updateMapping(dt)
