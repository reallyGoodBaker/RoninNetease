from ..architect.plugins.input.enum import ValueType
from ..architect.plugins.input.utils.inputAction import InputAction
from ..architect.plugins.input.utils.modifier import DeadZone


InputAction(
    'laravelMovement', ValueType.Vector2,
    modifiers=[
        DeadZone()
    ]
)