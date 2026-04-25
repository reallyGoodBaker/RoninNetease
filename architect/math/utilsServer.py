from .mat4 import identity, inverse, transformPoint, transform
from ..math.vec3 import vec, add, div, normalize, tup
from ..level.server import LevelServer
from ..core.basic import compServer, serverApi, defaultFilters, Location
from mod.common.minecraftEnum import EntityType

import math


def pointInBox(point, box):
    # type: (tuple[float, float, float], tuple[float, float, float]) -> bool
    # box 参数是盒子的全尺寸 (width, height, depth)
    # 假设盒子以原点为中心，范围从 -size/2 到 size/2
    size = box
    half_x = size[0] / 2
    half_y = size[1] / 2
    half_z = size[2] / 2
    return -half_x <= point[0] <= half_x and -half_y <= point[1] <= half_y and -half_z <= point[2] <= half_z


def boxOverlap3dServer(pos, rot, size, dim, filter=None):
    # type: (tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], int, function) -> list[str]
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
    firstFind = LevelServer.game.GetEntitiesInSquareArea(None, xozProjStart, xozProjEnd, dim)
    worldMatrix = inverse(transform(
        identity(),
        vec(pos),
        vec(rot),
        vec(size)
    ))
    result = []
    for entityId in firstFind:
        posComp = compServer.CreatePos(entityId)
        centerPos = div(add(vec(posComp.GetPos()), vec(posComp.GetFootPos())), 2)
        modelCenterPos = transformPoint(worldMatrix, centerPos)
        if pointInBox(modelCenterPos, size) and (filter is None or filter(entityId)):
            result.append(entityId)

    return result


def boxOverlap3dForward(entityId, size, debug=False):
    # type: (str, tuple[float, float, float], bool) -> list[str]
    """
    :param: size: (width, height, depth)
    """
    pos = compServer.CreatePos(entityId).GetPos()
    dir = forward(entityId)
    rot = serverApi.GetRotFromDir(tup(dir))
    result = boxOverlap3dServer(
        add(vec(pos), dir * 2).ToTuple(),
        (math.radians(rot[0]), -math.radians(rot[1]), 0), size, debug
    )
    if entityId in result:
        result.remove(entityId)
    return result

def boxOverlap3dFacing(entityId, size, debug=False):
    # type: (str, tuple[float, float, float], bool) -> list[str]
    """
    :param: size: (width, height, depth)
    """
    pos = compServer.CreatePos(entityId).GetPos()
    rot = compServer.CreateRot(entityId).GetRot()
    dir = serverApi.GetDirFromRot(rot)
    result = boxOverlap3dServer(
        add(vec(pos), vec(dir) * 2).ToTuple(),
        (math.radians(rot[0]), -math.radians(rot[1]), 0), size, debug
    )
    result.remove(entityId)
    return result


def facing(entityId):
    dir = serverApi.GetDirFromRot(compServer.CreateRot(entityId).GetRot())
    return vec(dir)


def forward(entityId, dist=1):
    rot = compServer.CreateRot(entityId).GetRot()
    if not rot:
        return vec((0, 0, 0))
    x, _, z = serverApi.GetDirFromRot(rot)
    return normalize(vec((x, 0, z))) * dist


def around(loc, radius):
    # type: (Location, float) -> list[str]
    pos = vec(loc.pos)
    dim = loc.dim
    radiusVec = vec((radius, radius, radius))
    return LevelServer.game.GetEntitiesInSquareArea(
        None, tup(pos - radiusVec), tup(pos + radiusVec), dim
    )