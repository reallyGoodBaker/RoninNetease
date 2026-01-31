from ...subsystem import ServerSubsystem, SubsystemServer
from ...event.server import EventListener
from ...basic import serverApi
from ..enhance.list import remove

@SubsystemServer
class PersonaServer(ServerSubsystem):

    def changePersona(self, id, renderConf):
        self.sendAllClients('PersonaChangeServer', {
            'id': id,
            'data': renderConf
        })

    def resetPersona(self, id):
        self.sendAllClients('PersonaResetServer', {
            'id': id,
        })

    @EventListener('BroadcastPersonaChange', isCustomEvent=True)
    def onPersonaChangeClient(self, ev):
        players = serverApi.GetPlayerList()
        remove(players, ev.__id__)
        self.sendClient(players, 'PersonaChangeClientAuthed', {
            'id': ev.id,
            'data': ev.data,
        })

    @EventListener('BroadcastPersonaReset', isCustomEvent=True)
    def onPersonaResetClient(self, ev):
        players = serverApi.GetPlayerList()
        remove(players, ev.__id__)
        self.sendClient(players, 'PersonaResetClientAuthed', {
            'id': ev.id,
        })
