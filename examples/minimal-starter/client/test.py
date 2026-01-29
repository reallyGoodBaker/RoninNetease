from ..architect.subsystem import ClientSubsystem, SubsystemClient
from ..architect.event.client import EventListener
from ..architect.event.core import ChainedEvent


@SubsystemClient
class TestSubsystem(ClientSubsystem):
    def onReady(self):
        print "Test subsystem client is ready!"

    @EventListener('OnLocalPlayerStopLoading')
    def onLocalPlayerStopLoading(self, event):
        # type: (ChainedEvent) -> None
        print "Local player stopped loading!