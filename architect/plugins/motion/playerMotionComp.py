from ....architect.compact import (
    Component, BaseCompClient, compClient, localPlayerId,
    tup, vec,
    remote,
)

@Component(singleton=True)
class PlayerMotionComponent(BaseCompClient):
    def onCreate(self, entityId):
        self.motionComp = compClient.CreateActorMotion(localPlayerId())

    @property
    def motion(self):
        return vec(self.motionComp.GetMotion())

    @motion.setter
    def motion(self, val):
        tMotion = tup(val)
        self.motionComp.SetMotion(tMotion)
        remote.client.call(
            'PlayerMotionSyncServer.syncMotion',
            tMotion
        )

    @property
    def inputVector(self):
        return self.motionComp.GetInputVector()
    
    @property
    def mousePosition(self):
        return self.motionComp.GetMousePosition()