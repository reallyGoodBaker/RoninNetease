# -*- coding: utf-8 -*-
import random as rand

def lerp(a, b, t):
    return a * (1 - t) + b * t

def clamp(x, min, max):
    return max if x > max else min if x < min else x

def smoothstep(edge0, edge1, x):
    # type: (float, float, float) -> float
    # https://en.wikipedia.org/wiki/Smoothstep
    # x in [edge0, edge1]
    t = clamp((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)

def alerp(start, end, t):
    diff = (end - start) % 360.0
    if diff > 180.0:
        diff -= 360.0
    elif diff < -180.0:
        diff += 360.0
    return start + diff * t

inf = 1e+10
epsilon = 1e-8

def random(min, max):
    return min + rand.random() * (max - min)

def normald(v):
    return v > 0 and 1 or v == 0 and 0 or -1