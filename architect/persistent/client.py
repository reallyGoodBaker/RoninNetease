from ..subsystem import ClientSubsystem, SubsystemClient
from ..level.client import LevelClient
from .common import DBSource

dbName = 'clientKVDb'
dbGlobalName = 'clientKVGlobal'

@SubsystemClient
class ClientKVDatabase(ClientSubsystem, DBSource):

    def __init__(self, system, engine, sysName):
        ClientSubsystem.__init__(self, system, engine, sysName)
        self.conf = LevelClient.getInst().configClient
        self.data = self.conf.GetConfigData(dbName)

    def getData(self, key):
        return self.data.get(key)
    
    def _save(self):
        self.conf.SetConfigData(dbName, self.data)
    
    def setData(self, key, value):
        self.data[key] = value
        self._save()

    def removeData(self, key):
        self.data.pop(key)
        self._save()

    def clearData(self):
        self.data = {}
        self._save()


@SubsystemClient
class ClientKVDatabaseGlobal(ClientSubsystem, DBSource):

    def __init__(self, system, engine, sysName):
        ClientSubsystem.__init__(self, system, engine, sysName)
        self.conf = LevelClient.getInst().configClient
        self.data = self.conf.GetConfigData(dbGlobalName, True)

    def getData(self, key):
        return self.data.get(key)
    
    def _save(self):
        self.conf.SetConfigData(dbGlobalName, self.data, True)
    
    def setData(self, key, value):
        self.data[key] = value
        self._save()

    def removeData(self, key):
        self.data.pop(key)
        self._save()

    def clearData(self):
        self.data = {}
        self._save()