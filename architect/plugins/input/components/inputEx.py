from ....compact import Component, BaseCompClient

class BoolInput(object):
    def __init__(self, lastPress, lastRelease):
        self.pressingKeys = {}
        self.inputStack = []

class FloatInput(object):
    def __init__(self):
        self.pressingKeys = {}
        self.inputStack = []

@Component(singleton=True)
class InputExComponent(BaseCompClient):
    def onCreate(self, _):
        self.keyboardPressing = {}
        self.mousePressing = {}
        self.gamepadPressing = {}
