# -*- coding: utf-8 -*-
__all__ = [
    'isPlayer',
    'getBonePosition',
    'getBoneRotation',
    'BonePositionTracker',
    'getBoneWorldPosAccurate',
]


from ..core.export import ClientSubsystem, SubsystemClient
from ..event import EventListener
from ..level.client import LevelClient, compClient
from mod.common.minecraftEnum import EntityType
from ..math.vec3 import vec
from ..utils.drawing import drawSphere

def isPlayer(entityId):
    return compClient.CreateEngineType(entityId).GetEngineType() == EntityType.Player

def getBonePosition(entityId, boneName, isLocal=False, particle='netease:tutorial_particle'):
    particleSystem = compClient.CreateParticleSystem(None)
    id = particleSystem.CreateBindEntityNew(particle, entityId, boneName)
    pos = vec(particleSystem.GetPos(id, isLocal))
    particleSystem.Remove(id)
    return pos

def getBoneWorldPosAccurate(entityId, boneName):
    model = compClient.CreateModel(entityId)
    return vec(model.GetBonePositionFromMinecraftObject(boneName))

def getBoneRotation(entityId, boneName, isLocal=False, particle='netease:tutorial_particle'):
    particleSystem = compClient.CreateParticleSystem(None)
    id = particleSystem.CreateBindEntityNew(particle, entityId, boneName)
    rot = vec(particleSystem.GetRot(id, isLocal))
    particleSystem.Remove(id)
    return rot

class BonePositionTracker(object):
    def __init__(self, entityId, boneName, particleName, isLocal=False):
        self.particle = compClient.CreateParticleSystem(None)
        self.entity = entityId
        self.bone = boneName
        self.parName = particleName
        self.parId = None
        self.isLocal = isLocal

    def exist(self):
        return self.particle.Exist(self.parId)

    def startTracking(self):
        if self.parId:
            return
        self.parId = self.particle.CreateBindEntityNew(self.parName, self.entity, self.bone)

    def getPosition(self):
        return vec(self.particle.GetPos(self.parId, self.isLocal))

    def getRotation(self):
        return vec(self.particle.GetRot(self.parId, self.isLocal))
    
    def stopTracking(self):
        if self.parId:
            self.particle.Remove(self.parId)
            self.parId = None

@SubsystemClient
class ClientUtilsSubsys(ClientSubsystem):

    def onInit(self):
        self.level = LevelClient.getInstance()

    @EventListener('PlayCustomAudio', isCustomEvent=True)
    def playSound(self, ev):
        entityId = ev.entityId
        entityPos = compClient.CreatePos(entityId).GetPos()
        self.level.customAudio.PlayCustomMusic(ev.sound, entityPos)

    @EventListener('StopCustomAudio', isCustomEvent=True)
    def stopSound(self, ev):
        self.level.customAudio.StopCustomMusic(ev.sound, 0.1)
