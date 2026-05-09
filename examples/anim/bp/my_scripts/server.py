from .architect.compact import *

@SubsystemServer
class AnimPlayerServer(ServerSubsystem):
    @Remote
    def cameraShake(self, playerId):
        runCommand('camera_shake {} 0.5 1 0.5'.format(playerId), playerId)

    @Remote
    def doAttack(self, playerId, entities, damage):
        for entityId in entities:
            compServer.CreateHurt(entityId).Hurt(damage, 'entity_attack', playerId)