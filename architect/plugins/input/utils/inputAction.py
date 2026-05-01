from ..enum import ValueType
from .modifier import InputModifier
from .trigger import InputTrigger

class InputAction(object):
    _registry = {}

    def __init__(self, name, valueType, triggers=[], modifiers=[]):
        # type: (str, ValueType, list[InputTrigger], list[InputModifier]) -> None
        self.name = name
        self.valueType = valueType
        self.modifiers = modifiers
        self.triggers = triggers

        if name in InputAction._registry:
            print('[WARN] InputAction: Action {} already registered'.format(name))
        InputAction._registry[name] = self

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)