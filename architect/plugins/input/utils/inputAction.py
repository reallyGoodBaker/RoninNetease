from ....core.log import warn as _log_warn
from ..enum import ValueType, AccumulationBehavior
from .modifier import InputModifier
from .trigger import InputTrigger

class InputAction(object):
    _registry = {}

    def __init__(self, name, valueType=ValueType.Vector3, triggers=[], modifiers=[], accBehavior=AccumulationBehavior.Cumulative):
        # type: (str, ValueType, list[InputTrigger], list[InputModifier], AccumulationBehavior) -> None
        self.name = name
        self.valueType = valueType
        self.accBehavior = accBehavior
        self.modifiers = modifiers
        self.triggers = triggers

        if name in InputAction._registry:
            _log_warn('InputAction: Action {} already registered', name)
        InputAction._registry[name] = self

    @classmethod
    def get(cls, name):
        # type: (str) -> InputAction
        return cls._registry.get(name)