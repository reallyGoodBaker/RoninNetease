from ....compact import Component, BaseCompClient

@Component()
class AnimationDilation(BaseCompClient):
    def onCreate(self, _):
        self.value = 1