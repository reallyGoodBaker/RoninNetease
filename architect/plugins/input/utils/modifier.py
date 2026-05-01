from ..enum import AxisSwizzleOrder


class InputModifier(object):
    def doModify(self, rawValue):
        # type: (tuple[float, float, float]) -> tuple[float, float, float]
        return rawValue


class Negate(InputModifier):
    def doModify(self, rawValue):
        if isinstance(rawValue, (int, float)):
            return -rawValue
        return rawValue


class Scale(InputModifier):
    def __init__(self, factor=1.0):
        self.factor = factor

    def doModify(self, rawValue):
        if isinstance(rawValue, (int, float)):
            return rawValue * self.factor
        return rawValue


class DeadZone(InputModifier):
    def __init__(self, lowerThreshold=0.2, upperThreshold=0.95):
        self.lower = lowerThreshold
        self.upper = upperThreshold

    def doModify(self, rawValue):
        if not isinstance(rawValue, (int, float)):
            return rawValue
        absVal = abs(rawValue)
        if absVal < self.lower:
            return 0.0
        if absVal > self.upper:
            return 1.0 if rawValue > 0 else -1.0
        t = (absVal - self.lower) / (self.upper - self.lower)
        return t if rawValue > 0 else -t


class SwizzleAxis(InputModifier):
    def __init__(self, order=AxisSwizzleOrder.XYZ):
        # type: (AxisSwizzleOrder) -> None
        self.order = order

    def doModify(self, rawValue):
        x, y, z = rawValue
        if self.order == AxisSwizzleOrder.XYZ:
            return x, y, z
        elif self.order == AxisSwizzleOrder.YZX:
            return y, z, x
        elif self.order == AxisSwizzleOrder.ZXY:
            return z, x, y
        elif self.order == AxisSwizzleOrder.XZY:
            return x, z, y
        elif self.order == AxisSwizzleOrder.YXZ:
            return y, x, z
        elif self.order == AxisSwizzleOrder.ZYX:
            return z, y, x
        return rawValue