# -*- coding: utf-8 -*-
from .....architect.compact import (
    ServerSubsystem, SubsystemServer,
    Remote,
    compServer,
)

@SubsystemServer
class PlayerMotionSyncServer(ServerSubsystem):

    @Remote
    def syncMotion(self, playerId, motion):
        compServer.CreateActorMotion(playerId).SetPlayerMotion(motion)
