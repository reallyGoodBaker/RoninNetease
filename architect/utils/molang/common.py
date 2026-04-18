from ...core.basic import isServer, compClient, compServer
from ...core.unreliable import Unreliable
from .types import MolangReadable, MolangMutable


class NamedVariable(Unreliable, MolangMutable):
    def __init__(self, name):
        Unreliable.__init__(self)
        self.name = name

    def _molangComp(self, actorId):
        if isServer():
            return compServer.CreateQueryVariable(actorId)
        else:
            return compClient.CreateQueryVariable(actorId)

    def getValue(self, actorId, defaultValue=0):
        molang = self._molangComp(actorId)
        result = molang.EvalMolangExpression('v.' + self.name)
        if result.get('error'):
            self._handleError(result['error'])
            return defaultValue
        return result['value']
    
    def setValue(self, actorId, value):
        molang = self._molangComp(actorId)
        molang.EvalMolangExpression('variable.{} = {};'.format(self.name, value))
