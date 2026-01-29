from ..architect.subsystem import ServerSubsystem, SubsystemServer


@SubsystemServer
class TestSubsystem(ServerSubsystem):
    def onReady(self):
        print "Test subsystem server is ready!"