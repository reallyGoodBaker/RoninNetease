from .architect.compact import *
from .architect.plugins.animation.components.animClient import AnimationExComponent, AnimationEasingTypes, AnimationEasingConf
from .architect.utils.persona.client import PersonaRendererComponent

from .assets.animations import GenericMapping

PlayerPersona = {
    'geometry': {
        'default': 'geometry.standard_steve'
    },
    'animations': {
        'root': 'animation.standard_steve.idle'
    },
    'scripts': {
        'animate': [
            { 'root' }
        ]
    }
}

ItemHoldingAnimMapping = {
    'minecraft:diamond_sword': 'diamond',
    'minecraft:wooden_sword': 'wood',
    'minecraft:iron_sword': 'iron',
}

@SubsystemClient
class AnimPlayerClient(ClientSubsystem):
    def onInit(self):
        self.moveInputing = False

    @EventListener()
    def onPlayerSwap(self, ev=events.OnCarriedNewItemChangedClientEvent()):
        name = ev.itemDict['newItemName']
        animKey = ItemHoldingAnimMapping.get(name, 'idle')
        animEx = getOneComponent(localPlayerId(), AnimationExComponent)
        if animEx:
            animEx.play(animKey, 'holding')

    @EventListener()
    def onPlayerCreated(self, ev=events.AddPlayerCreatedClientEvent()):
        id = ev.playerId
        animEx = getOrCreateComponent(id, AnimationExComponent)
        renderer = getOrCreateComponent(id, PersonaRendererComponent)
        renderer.addRenderConf(PlayerPersona, False)
        animEx.registerAnimations(GenericMapping)
        animEx.updateActorAnimDef()
        for animKey in GenericMapping.keys():
            animEx.registerEasing(
                animKey,
                AnimationEasingConf(1, 0.15, AnimationEasingTypes.SINE),
                AnimationEasingConf(0, 0.2, AnimationEasingTypes.SINE),
            )

    @Sched.Render()
    def onPlayerMove(self):
        actorMotion = compClient.CreateActorMotion(localPlayerId())
        x, z = actorMotion.GetInputVector()
        isMoving = x != 0 or z != 0
        if isMoving != self.moveInputing:
            self.broadcast('walk', { 'moving': isMoving })
            self.moveInputing = isMoving

    @CustomEvent('walk')
    def onPlayerWalk(self, ev):
        moving = ev.moving
        animEx = getOneComponent(localPlayerId(), AnimationExComponent)
        if moving:
            animEx.play('walk', 'loco')
        else:
            animEx.stop('walk', 'loco')