from ...component import BaseCompServer, Component
from ...event import ChainedEvent

@Component(singleton=True)
class EventReader(BaseCompServer):
    def onCreate(self, _):
        self.ev = None

    def event(self):
        # type: () -> ChainedEvent
        return self.ev