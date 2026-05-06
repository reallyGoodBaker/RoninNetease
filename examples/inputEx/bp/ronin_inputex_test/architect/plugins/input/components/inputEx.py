from ....compact import Component, BaseCompClient
from ..utils.inputValue import InputValue


@Component(singleton=True)
class InputExComponent(BaseCompClient):
    def onCreate(self, _):
        self._rawInputs = {} # type: dict[tuple[str, str], InputValue]
        self.actionValues = {} # type: dict[str, tuple[int, float|tuple[float, float, float]|tuple[float, float]]]

    def updateInputValue(self, inputType, key, value):
        mappingKey = (inputType, key)
        if mappingKey not in self._rawInputs:
            self._rawInputs[mappingKey] = InputValue(value)
        else:
            self._rawInputs[mappingKey].rawValue = value
        
    def getInputValue(self, inputType, key):
        mappingKey = (inputType, key)
        if mappingKey not in self._rawInputs:
            return InputValue()
        return self._rawInputs[mappingKey]