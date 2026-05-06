from ..architect.plugins.input.enum import InputType, KeyboardKey, AxisSwizzleOrder, GamepadAxis
from ..architect.plugins.input.utils.mappingContext import InputMapping, InputBinding
from ..architect.plugins.input.utils.modifier import SwizzleAxis, Negate
from ..architect.plugins.input.utils.trigger import TriggerDown


InputMapping(
    'move', [
        InputBinding(
            InputType.Key, KeyboardKey.W,
            'laravelMovement',
            # 键盘输入的值不是布尔值, 而是一个Vector3, (isDown, 0.0, 0.0), 通过把x换到y轴，可以实现两个轴的复合输入
            modifiers=[ SwizzleAxis(order=AxisSwizzleOrder.YXZ) ],
            triggers=[ TriggerDown() ],
        ),
        InputBinding(
            InputType.Key, KeyboardKey.S,
            'laravelMovement',
            modifiers=[
                SwizzleAxis(order=AxisSwizzleOrder.YXZ),
                # 键盘输入的值只能是0.0或者1.0, 所以把值取反就能得到一个轴的正负方向输入
                Negate()
            ],
            triggers=[ TriggerDown() ],
        ),
        InputBinding(
            InputType.Key, KeyboardKey.D,
            'laravelMovement',
            triggers=[ TriggerDown() ],
        ),
        InputBinding(
            InputType.Key, KeyboardKey.A,
            'laravelMovement',
            modifiers=[ Negate() ],
            triggers=[ TriggerDown() ],
        ),
        InputBinding(
            # 由于我们的wasd输入轴的布局和手柄输入轴完全一致，这里手柄输入可以不做修改
            InputType.Axis, GamepadAxis.LS,
            'laravelMovement',
            triggers=[ TriggerDown() ],
        )
    ]
)