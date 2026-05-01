import math

from ..enum import ValueType


class InputValue(object):
    def __init__(self, defaultValue=(0.0, 0.0, 0.0)):
        self.rawValue = defaultValue # type: tuple[float, float, float]

    def size(self):
        x, y, z = self.rawValue
        return math.sqrt(x*x + y*y + z*z)

    def value(self, type=ValueType.Vector3):
        if type == ValueType.Vector3:
            return self.rawValue
        elif type == ValueType.Vector2:
            return self.rawValue[:2]
        elif type == ValueType.Double:
            return self.rawValue[0]
        else:
            return None