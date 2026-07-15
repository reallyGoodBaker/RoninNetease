# -*- coding: utf-8 -*-
import math

class interpolators:
    linear = staticmethod(lambda x, y, t: x + (y - x) * t)
    quad = staticmethod(lambda x, y, t: x + (y - x) * t * t * (3 - 2 * t))
    cubic = staticmethod(lambda x, y, t: x + (y - x) * (6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3))
    quart = staticmethod(lambda x, y, t: x + (y - x) * (-20 * t ** 7 + 70 * t ** 6 - 84 * t ** 5 + 35 * t ** 4))

    linearSphere = staticmethod(lambda x, y, t: x + (y - x) * t * (1 - math.sqrt(1 - t * t)))

    @staticmethod
    def bezier(p1):
        return lambda x, y, t: (1 - t) ** 2 * x + 2 * (1 - t) * t * p1 + t ** 2 * y

    @staticmethod
    def cubicBezier(p1, p2):
        return lambda x, y, t: (1 - t) ** 3 * x + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * y

    @staticmethod
    def bounce(x, y, t):
        if t < 1 / 2.75:
            return x + (y - x) * 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return x + (y - x) * (7.5625 * t * t + 0.75)
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return x + (y - x) * (7.5625 * t * t + 0.9375)
        else:
            t -= 2.625 / 2.75
            return x + (y - x) * (7.5625 * t * t + 0.984375)

    easeIn = staticmethod(lambda x, y, t: x + (y - x) * t * t)
    easeOut = staticmethod(lambda x, y, t: x + (y - x) * (1 - (1 - t) * (1 - t)))
    easeInOut = staticmethod(lambda x, y, t: x + (y - x) * (t * t * (3 - 2 * t)))

    @staticmethod
    def combine(fn1, fn2, ratio=0.5):
        return lambda x, y, t: fn1(x, y, t) * ratio + fn2(x, y, t) * (1 - ratio)

    @staticmethod
    def catmullRom(x, y, t):
        p0, p1, p2, p3 = x, x, y, y
        return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)
