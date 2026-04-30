from ..math.vec3 import Vector3, vec, cross, normalize
from ..level.client import LevelClient, compClient
from ..core.basic import levelId

def drawLine(start, end, color, duration=5):
    # type: (Vector3, Vector3, Vector3, float) -> None
    game = LevelClient.getInstance().game
    drawing = compClient.CreateDrawing(levelId())
    shape = drawing.AddLineShape(
        (start.x, start.y, start.z),
        (end.x, end.y, end.z),
        (color.x, color.y, color.z),
        duration
    )
    game.AddTimer(duration, lambda: shape.Remove())

def drawBox(start, size, forward, color, duration=5):
    # type: (Vector3, Vector3, Vector3, tuple, float) -> None
    right = normalize(cross(forward, vec((0, 1, 0))))
    up = normalize(cross(right, forward))

    _forward = forward * size.z
    _up = up * size.y
    _right = right * size.x

    # 8个顶点
    vertices = [
        start + _forward + _up + _right,
        start - _forward + _up + _right,
        start - _forward - _up + _right,
        start + _forward - _up + _right,
        start + _forward + _up - _right,
        start - _forward + _up - _right,
        start - _forward - _up - _right,
        start + _forward - _up - _right
    ]

    # 12条线
    lines = [
        (vertices[0], vertices[1]),
        (vertices[1], vertices[2]),
        (vertices[2], vertices[3]),
        (vertices[3], vertices[0]),
        (vertices[4], vertices[5]),
        (vertices[5], vertices[6]),
        (vertices[6], vertices[7]),
        (vertices[7], vertices[4]),
        (vertices[0], vertices[4]),
        (vertices[1], vertices[5]),
        (vertices[2], vertices[6]),
        (vertices[3], vertices[7])
    ]

    for line in lines:
        drawLine(line[0], line[1], color, duration)