from ..architect.subsystem import ClientSubsystem, SubsystemClient


@SubsystemClient
class TestSubsystem(ClientSubsystem):
    def onReady(self):
        print "Test subsystem client is ready!"