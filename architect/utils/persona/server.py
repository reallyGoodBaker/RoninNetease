from ...subsystem import ServerSubsystem, SubsystemServer
from ...event.server import EventListener
from ...basic import serverApi

@SubsystemServer
class PersonaServer(ServerSubsystem):

    def changePersona(self, id, renderConf):
        self.sendAllClients('PersonaChangeServer', {
            'id': id,
            'data': renderConf
        })

    def broadcastPersona(self, id, renderConf):
        allPlayers = serverApi.GetPlayerList()
        if id in allPlayers:
            allPlayers.remove(id)

        self.sendClient(allPlayers, 'PersonaChangeServer', {
            'id': id,
            'data': renderConf
        })

    def resetPersona(self, id):
        self.sendAllClients('PersonaResetServer', {
            'id': id
        })

    def addPlayerPreloadMapping(self, mapping):
        self.sendAllClients('PlayerAddPreloadMappingServer', {
            'id': id,
            'mapping': mapping,
        })

    def changePlayerPreload(self, id, preloadId):
        self.sendAllClients('PlayerChangePreloadServer', {
            'id': id,
            'preloadId': preloadId,
        })

    @EventListener('PersonaChangeClient', isCustomEvent=True)
    def onPersonaChangeClient(self, ev):
        self.changePersona(ev.id, ev.data)

    @EventListener('PersonaResetClient', isCustomEvent=True)
    def onPersonaResetClient(self, ev):
        self.resetPersona(ev.id)
