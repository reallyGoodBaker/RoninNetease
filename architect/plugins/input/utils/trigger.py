from ..enum import TriggerState, TriggerCombineType


class InputTrigger(object):
    """Base class for input triggers.
    Determines when an action event is fired based on input state changes.
    """
    combineType = TriggerCombineType.Or
    def updateState(self, inputVal, deltaTime=0.0):
        # type: (InputTrigger, object, float) -> TriggerState
        """Check if this trigger condition is met.
        Returns True if the action should fire.
        """
        return TriggerState.Ongoing


class TriggerDown(InputTrigger):
    combineType = TriggerCombineType.Or
    def updateState(self, rawValue, deltaTime=0.0):
        if rawValue.size() > 0:
            return TriggerState.Triggered
        return TriggerState.Empty


class TriggerPressed(InputTrigger):
    combineType = TriggerCombineType.Or

    def __init__(self):
        self._wasPressed = False

    def updateState(self, rawValue, deltaTime=0.0):
        pressed = rawValue.size()
        triggered = pressed and not self._wasPressed
        self._wasPressed = pressed
        return TriggerState.Triggered if triggered else TriggerState.Empty


class TriggerReleased(InputTrigger):
    combineType = TriggerCombineType.Or

    def __init__(self):
        self._wasPressed = False

    def updateState(self, rawValue, deltaTime=0.0):
        pressed = rawValue.size()
        triggered = not pressed and self._wasPressed
        self._wasPressed = pressed
        return TriggerState.Triggered if triggered else TriggerState.Empty


class TriggerHold(InputTrigger):
    combineType = TriggerCombineType.Or

    def __init__(self, holdTime=0.5):
        self.holdTime = holdTime
        self._timer = 0.0
        self._wasPressed = False
        self._fired = False

    def updateState(self, rawValue, deltaTime=0.0):
        pressed = rawValue.size() > 0
        if pressed:
            if not self._wasPressed:
                self._timer = 0.0
                self._fired = False
            else:
                self._timer += deltaTime
                if not self._fired and self._timer >= self.holdTime:
                    self._fired = True
                    self._wasPressed = pressed
                    return TriggerState.Triggered
            return TriggerState.Ongoing
        else:
            self._timer = 0.0
            self._fired = False
        self._wasPressed = pressed
        return TriggerState.Empty


class TriggerTap(InputTrigger):
    """Fires if the key is pressed and released within a specified time window."""
    combineType = TriggerCombineType.Or

    def __init__(self, tapTime=0.2):
        self.tapTime = tapTime
        self._timer = 0.0
        self._isDown = False

    def updateState(self, rawValue, deltaTime=0.0):
        pressed = rawValue.size() > 0
        if pressed and not self._isDown:
            self._timer = 0.0
            self._isDown = True
            return TriggerState.Ongoing
        if self._isDown:
            if pressed:
                self._timer += deltaTime
                return TriggerState.Ongoing
            else:
                self._isDown = False
                if self._timer <= self.tapTime:
                    self._timer = 0.0
                    return TriggerState.Triggered
                self._timer = 0.0
        return TriggerState.Empty


class TriggerCombo(InputTrigger):
    """Fires if all the specified triggers are triggered within a specified time window."""
    combineType = TriggerCombineType.And

    def __init__(self, triggers, comboTime=0.2):
        self.triggers = triggers
        self.comboTime = comboTime
        self._timer = 0.0
        self._fired = False

    def updateState(self, rawValue, deltaTime=0.0):
        if self._fired:
            return TriggerState.Empty
        if self._timer > self.comboTime:
            self._timer = 0.0
            self._fired = True
            return TriggerState.Triggered
        self._timer += deltaTime
        for trigger in self.triggers:
            if trigger.updateState(rawValue, deltaTime) == TriggerState.Triggered:
                return TriggerState.Ongoing
        return TriggerState.Empty