from ...component import BaseCompClient, Component
from ...event import ChainedEvent

@Component(singleton=True)
class EventReader(BaseCompClient):
    def onCreate(self, _):
        self.ev = None

    def event(self):
        # type: () -> ChainedEvent
        return self.ev