from .enum import ValueType

class InputAction(object):
    registeredActions = {}

    def __init__(self, name, valueType, *triggers):
        # type: (str, ValueType, *str) -> None
        self.name = name
        self.valueType = valueType
        self.triggers = triggers

        if name in InputAction.registeredActions:
            print('[WARN] InputAction: Action {} already registered')
        InputAction.registeredActions[name] = self
