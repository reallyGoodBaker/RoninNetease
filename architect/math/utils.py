from .mat4 import worldToScreen, identity, lookAt, perspective, screenToWorld, inverse, Matrix, transformPoint, transform, rotateAxis, translate, scale
from ..math.vec3 import vec, modulo, Vector3, add, div
from ..level.client import LevelClient, clientApi

import math

level = LevelClient.getInstance()
screenWidth, screenHeight = level.game.GetScreenSize()

def localViewMatrix():
    camPos = level.camera.GetPosition()
    camForward = level.camera.GetForward()
    target = (
        camPos[0] + camForward[0],
        camPos[1] + camForward[1],
        camPos[2] + camForward[2],
    )
    return lookAt(
        vec(camPos),
        vec(target),
        vec((0, 1, 0))
    )

def localProjectionMatrix():
    return perspective(
        level.camera.GetFov(),
        screenWidth / screenHeight,
        0.1,
        100
    )

def worldPosToScreenPos(worldPoint):
    # type: (tuple[float, float, float]) -> Vector3
    return worldToScreen(
        identity(),
        localViewMatrix(),
        localProjectionMatrix(),
        (screenWidth, screenHeight),
        vec(worldPoint)
    )

def screenPosToWorldPos(screenPoint, depth):
    # type: (tuple[float, float], float) -> Vector3
    pointVec = vec((screenPoint[0], screenPoint[1], 0))
    return screenToWorld(
        identity(),
        localViewMatrix(),
        localProjectionMatrix(),
        (screenWidth, screenHeight),
        pointVec,
        depth
    )

defaultFilters = {
    "any_of": [
        {
            "subject" : "other",
            "test" :  "is_family",
            "value" :  "player"
        },
        {
            "subject" : "other",
            "test" :  "is_family",
            "value" :  "mob"
        }
    ]
}

from ..core.basic import compClient, compServer
from ..level.client import LevelClient
from ..level.server import LevelServer

level = LevelClient.getInstance()

def pointInBox(point, box):
    # type: (tuple[float, float, float], tuple[float, float, float]) -> bool
    # box 参数是盒子的全尺寸 (width, height, depth)
    # 假设盒子以原点为中心，范围从 -size/2 到 size/2
    size = box
    half_x = size[0] / 2
    half_y = size[1] / 2
    half_z = size[2] / 2
    return -half_x <= point[0] <= half_x and -half_y <= point[1] <= half_y and -half_z <= point[2] <= half_z

def pointInAabb(point, min, max):
    # type: (tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]) -> bool
    return min[0] <= point[0] <= max[0] and min[1] <= point[1] <= max[1] and min[2] <= point[2] <= max[2]

def boxOverlap3dClient(pos, rot, size, debug=False):
    # type: (tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], bool) -> list[str]
    radius = math.ceil(math.sqrt(size[0] ** 2 + size[2] ** 2))
    x, y, z = pos
    xozProjStart = (
        x - radius,
        y - radius,
        z - radius
    )
    xozProjEnd = (
        x + radius,
        y + radius,
        z + radius
    )
    firstFind = level.game.GetEntitiesInSquareArea(None, xozProjStart, xozProjEnd)
    worldMatrix = inverse(transform(
        identity(),
        vec(pos),
        vec(rot),
        vec(size)
    ))
    result = []
    for entityId in firstFind:
        posComp = compClient.CreatePos(entityId)
        centerPos = div(add(vec(posComp.GetPos()), vec(posComp.GetFootPos())), 2)
        modelCenterPos = transformPoint(worldMatrix, centerPos)
        if pointInBox(modelCenterPos, size):
            result.append(entityId)

    return result


def boxOverlap3dForward(entityId, size):
    pos = compClient.CreatePos(entityId).GetPos()
    rot = compClient.CreateRot(entityId).GetRot()
    dir = clientApi.GetDirFromRot(rot)
    result = boxOverlap3dClient(
        add(vec(pos), vec(dir) * 2).ToTuple(),
        (rot[0], rot[1], 0), size,
    )
    result.remove(entityId)
    return result


def forward(entityId):
    x, _, z = clientApi.GetDirFromRot(compClient.CreateRot(entityId).GetRot())
    return vec((x, 0, z)).Normalized()


def facing(entityId):
    dir = clientApi.GetDirFromRot(compClient.CreateRot(entityId).GetRot())
    return vec(dir)

def entityAabbDef(entityId):
    molang = compClient.CreateQueryVariable(entityId)
    molang.EvalMolangExpression("t.aabb = q.bone_aabb('head'); t.min = t.aabb.min; t.max = t.aabb.max;")
    mx = molang.EvalMolangExpression("t.min.x")['value'] / 16
    my = molang.EvalMolangExpression("t.min.y")['value'] / 16
    mz = molang.EvalMolangExpression("t.min.z")['value'] / 16
    px = molang.EvalMolangExpression("t.max.x")['value'] / 16
    py = molang.EvalMolangExpression("t.max.y")['value'] / 16
    pz = molang.EvalMolangExpression("t.max.z")['value'] / 16
    return (mx, my, mz), (px, py, pz)