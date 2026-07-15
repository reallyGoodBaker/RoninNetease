# -*- coding: utf-8 -*-
from .interpolators import interpolators


class Curve(object):
    def __init__(self, points, interpolator=interpolators.linear):
        # type: (list[tuple[float, object]], interpolators) -> None
        self.points = sorted(points)
        self.interp = interpolator

    def getValue(self, x):
        # type: (float) -> object
        points = self.points
        n = len(points)

        if n == 0:
            raise ValueError("Curve has no points")

        if x <= points[0][0]:
            return points[0][1]

        if x >= points[-1][0]:
            return points[-1][1]

        lo, hi = 0, n - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if x < points[mid][0]:
                hi = mid
            else:
                lo = mid

        x0, y0 = points[lo]
        x1, y1 = points[hi]
        t = (x - x0) / (x1 - x0)

        return self.interp(y0, y1, t)